from pathlib import Path
from typing import Literal

from deeppresenter.agents.agent import Agent, AgentEnv
from deeppresenter.utils.config import DeepPresenterConfig
from deeppresenter.utils.constants import MAX_SUBAGENT_TURNS


class SubAgent(Agent):
    @classmethod
    def delegate(
        cls,
        config: DeepPresenterConfig,
        agent_env: AgentEnv,
        workspace: Path,
        language: Literal["zh", "en"],
    ):
        async def delegate_subagent(short: str, task: str, context_file: str):
            """
            Delegate a self-contained subtask to a fresh subagent with an isolated workspace.

            Args:
                short: Short unique task id, search_01 for example.
                task: Minimal action instruction for this subtask.
                context_file: Path to a local file that stores the full delegation context.
            """
            context_path = Path(context_file)
            sub_workspace = workspace / "subagents" / short
            if sub_workspace.exists():
                raise Exception("Should not use the same short for more than once")
            sub_workspace.mkdir(parents=True)
            subagent = cls(
                config, agent_env, sub_workspace, language, max_turns=MAX_SUBAGENT_TURNS
            )
            subagent.name = short
            if not context_path.is_absolute():
                context_path = workspace / context_path
            assert context_path.exists(), f"Context file {context_file} does not exist"
            try:
                return await subagent.loop(task, context_path.read_text())
            finally:
                subagent.save_history()

        return delegate_subagent

    async def loop(self, task: str, context: str):
        while True:
            await self.action(task=task, context=context)
            outcome = await self.execute(self.chat_history[-1].tool_calls)
            if not isinstance(outcome, list):
                return outcome
