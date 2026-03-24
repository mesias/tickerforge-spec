from importlib.resources import files
from importlib.metadata import version as metadata_version
from pathlib import Path


def get_spec_root() -> Path:
    """Directory containing canonical spec (exchanges/, contracts/, schemas/, tests/, ...)."""
    here = Path(__file__).resolve().parent
    bundled = here / "spec"
    if bundled.is_dir() and (bundled / "schemas").is_dir():
        return bundled
    repo = here.parent / "spec"
    if repo.is_dir() and (repo / "schemas").is_dir():
        return repo
    raise RuntimeError(
        "tickerforge_spec_data: spec tree not found (expected vendored spec/ or repo-root spec/)."
    )


def get_version() -> str:
    return metadata_version("tickerforge-spec-data")
