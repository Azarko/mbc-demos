import contextlib
import logging
import os
import uuid

import imaginator.entry as imaginator_entry


logger = logging.getLogger(__name__)


def generate_video(text: str) -> bytes:
    logger.info(f'start generating video for text "{text}')
    filename = f'{uuid.uuid4().hex}.mp4'
    try:
        imaginator = imaginator_entry.Imaginator()
        imaginator_entry.create_video(
            imaginator=imaginator,
            name=filename,
            text_line=text,
        )
        return _load_result(filename)
    finally:
        with contextlib.suppress(OSError):
            os.remove(filename)


def _load_result(path: str) -> bytes:
    with open(path, 'rb') as stream:
        return stream.read()
