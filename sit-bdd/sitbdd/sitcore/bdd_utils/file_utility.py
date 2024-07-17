__all__ = ["temporary_file"]

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def temporary_file(suffix=None) -> Iterator[Path]:
    """
    Create a temporary file. This is a context manager, and the file will be
    deleted when the manager exits.
    :param suffix: Optional ending to the generated filename.
    :return: File path.
    """

    descriptor, raw_path = tempfile.mkstemp(suffix=suffix)
    path = Path(raw_path)
    try:
        yield path
    finally:
        os.close(descriptor)
        path.unlink()
