from os.path import join

from test.conftest import test_config

from pptagent.multimodal import ImageLabler
from pptagent.presentation import Presentation


def test_load_captions():
    prs = Presentation.from_file(
        join(test_config.template, "source.pptx"), test_config.config
    )
    image_labler = ImageLabler(prs, test_config.config)
    image_labler.apply_stats(test_config.get_image_stats())
