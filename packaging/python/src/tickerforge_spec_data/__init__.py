from __future__ import annotations

from importlib.metadata import version as metadata_version
from importlib.resources import files
from pathlib import Path


def get_spec_root() -> Path:
    return Path(str(files("tickerforge_spec_data").joinpath("spec")))


def get_version() -> str:
    return metadata_version("tickerforge-spec-data")
