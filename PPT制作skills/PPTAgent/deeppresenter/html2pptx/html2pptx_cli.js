const fs = require("node:fs");
const path = require("node:path");

// Add local node_modules to module search path
const localNodeModules = path.join(__dirname, "node_modules");
if (fs.existsSync(localNodeModules)) {
  module.paths.unshift(localNodeModules);
}

const fg = require("fast-glob");
const minimist = require("minimist");
const pptxgen = require("pptxgenjs");
const html2pptx = require("./html2pptx");

const LAYOUT_MAP = {
  "16:9": "LAYOUT_WIDE",
  "4:3": "LAYOUT_4x3",
};

const A1_LAYOUT = {
  name: "A1",
  width: 23.39,
  height: 33.11,
};

const A2_LAYOUT = {
  name: "A2",
  width: 16.54,
  height: 23.39,
};

const A3_LAYOUT = {
  name: "A3",
  width: 11.69,
  height: 16.54,
};

const A4_LAYOUT = {
  name: "A4",
  width: 8.27,
  height: 11.69,
};

async function run() {
  const args = minimist(process.argv.slice(2));
  const layout = args.layout || "auto";
  const outputFile = args.output;
  const validateOnly = Boolean(args.validate);
  const softMode = Boolean(args.soft);
  const htmlDir = args.html_dir || args["html-dir"];
  let htmlFiles = [];

  if (args.html) {
    htmlFiles = Array.isArray(args.html) ? args.html : String(args.html).split(",");
    htmlFiles = htmlFiles.map((file) => path.resolve(file.trim())).filter(Boolean);
  }

  if (htmlDir && htmlFiles.length) {
    console.error("Use either --html_dir or --html, not both.");
    process.exit(1);
  }

  if (htmlDir) {
    if (!fs.existsSync(htmlDir) || !fs.statSync(htmlDir).isDirectory()) {
      console.error(`HTML directory not found: ${htmlDir}`);
      process.exit(1);
    }
    htmlFiles = fg.sync("*.html", { cwd: htmlDir, absolute: true }).sort();
  }

  if (!htmlFiles.length) {
    console.error(
      "Usage: node html2pptx_cli.js --html_dir <dir> | --html <file> [--html <file2>] --output <file.pptx> --layout <auto|16:9|4:3|A1|A2|A3|A4> [--author <name>] [--title <title>] [--subject <subject>] [--company <company>] [--revision <rev>] [--validate] [--soft]"
    );
    process.exit(1);
  }

  if (!validateOnly && !outputFile) {
    console.error("Missing --output for PPTX generation.");
    process.exit(1);
  }

  const pptx = new pptxgen();
  pptx.author = args.author || "DeepPresenter";
  pptx.title = args.title || "DeepPresenter Presentation";
  pptx.subject = args.subject || "";
  pptx.company = args.company || "DeepPresenter";
  if (args.revision) pptx.revision = args.revision;

  if (layout === "auto") {
    // Layout will be auto-adapted from HTML body dimensions by html2pptx
  } else if (layout === "A1") {
    pptx.defineLayout(A1_LAYOUT);
    pptx.layout = "A1";
    pptx._html2pptx_layoutLocked = true;
  } else if (layout === "A2") {
    pptx.defineLayout(A2_LAYOUT);
    pptx.layout = "A2";
    pptx._html2pptx_layoutLocked = true;
  } else if (layout === "A3") {
    pptx.defineLayout(A3_LAYOUT);
    pptx.layout = "A3";
    pptx._html2pptx_layoutLocked = true;
  } else if (layout === "A4") {
    pptx.defineLayout(A4_LAYOUT);
    pptx.layout = "A4";
    pptx._html2pptx_layoutLocked = true;
  } else if (LAYOUT_MAP[layout]) {
    pptx.layout = LAYOUT_MAP[layout];
    pptx._html2pptx_layoutLocked = true;
  } else {
    console.error(`Unsupported layout: ${layout}`);
    process.exit(1);
  }

  for (const htmlFile of htmlFiles) {
    await html2pptx(htmlFile, pptx, { soft: softMode });
  }

  if (!validateOnly) {
    const outputPath = path.resolve(outputFile);
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    await pptx.writeFile({ fileName: outputPath });
  }
}

run().catch((err) => {
  console.error(err?.stack || err?.message || String(err));
  process.exit(1);
});
