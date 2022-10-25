import os
from pathlib import Path, PurePath
import shutil


def copy_file(source_path: str, output_path: str) -> None:
    """
    Copy source_path to output_path, making sure any parent directories exist.
    The output_path may be a directory.
    """
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    if os.path.isdir(output_path):
        output_path = output_path.join(PurePath(source_path).name)
    shutil.copyfile(source_path, output_path)
