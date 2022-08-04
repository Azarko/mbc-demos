import os.path
import uuid

import pytest

from mbc.utils import video_generator


UUID = uuid.UUID('00000000-0000-0000-0000-000000000000')


@pytest.fixture(name='patch_uuid')
def _patch_uuid(patch_method):
    @patch_method('uuid.uuid4')
    def generate_uuid(*args, **kwargs):
        return UUID


@pytest.mark.usefixtures('patch_uuid')
async def test_video_generator():
    result = video_generator.generate_video('text')
    assert result
    assert not os.path.isfile(f'{UUID.hex}.mp4')


@pytest.mark.usefixtures('patch_uuid')
async def test_video_generator_fail(patch_method):
    @patch_method('mbc.utils.video_generator._load_result')
    def _load_result(*args, **kwargs):
        raise ValueError

    with pytest.raises(ValueError):
        video_generator.generate_video('text')
    assert not os.path.isfile(f'{UUID.hex}.mp4')
