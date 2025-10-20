# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "beartype",
#     "tqdm",
#     "tyro",
# ]
# ///

"""
Downloads the ADE20K dataset archive from http://sceneparsing.csail.mit.edu/ and extracts it locally.

Run this script with

uv run ade20k_download.py
"""

import pathlib
import shutil
import urllib.request
import zipfile

import beartype
import tqdm

DEFAULT_URL = "http://data.csail.mit.edu/places/ADEchallenge/ADEChallengeData2016.zip"
EXPECTED_TOP_LEVEL_DIR = "ADEChallengeData2016"


def _download(url: str, target: pathlib.Path) -> None:
    """Download the dataset archive with a progress bar."""
    with urllib.request.urlopen(url) as response:  # noqa: S310 - trusted dataset host
        total_bytes = response.length
        if total_bytes is None:
            total_bytes = int(response.headers.get("Content-Length", 0))

        chunk_size = 1 << 20  # 1 MiB chunks to balance IO and progress updates.
        with (
            open(target, "wb") as fd,
            tqdm.tqdm(
                total=total_bytes or None,
                unit="B",
                unit_scale=True,
                desc=f"Downloading {target.name}",
            ) as progress,
        ):
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                fd.write(chunk)
                progress.update(len(chunk))


def _extract(zip_path: pathlib.Path, destination_parent: pathlib.Path) -> None:
    """Extract the dataset archive with a progress indicator."""
    with zipfile.ZipFile(zip_path) as archive:
        members = archive.infolist()
        with tqdm.tqdm(
            members, unit="file", desc=f"Extracting {zip_path.name}"
        ) as progress:
            for member in members:
                archive.extract(member, path=destination_parent)
                progress.update()


@beartype.beartype
def main(
    url: str = DEFAULT_URL,
    destination: pathlib.Path = pathlib.Path(".", "ADEChallengeData2016"),
    zip_path: pathlib.Path | None = None,
    overwrite: bool = False,
):
    """Download and extract ADE20K.

    Args:
        url: Location of the ADE20K archive.
        destination: Directory where the extracted dataset should live.
        zip_path: Optional explicit path for the downloaded zip file. Defaults to
            `destination` with a `.zip` suffix.
        overwrite: Replace existing archive or extracted directory if present.
    """
    destination = destination.expanduser()
    if destination.suffix.lower() == ".zip":
        raise ValueError("destination must be a directory, not a zip file path.")
    destination.parent.mkdir(parents=True, exist_ok=True)

    if zip_path is None:
        zip_path = destination.with_suffix(".zip")
    else:
        zip_path = zip_path.expanduser()

    zip_path.parent.mkdir(parents=True, exist_ok=True)

    if zip_path.exists() and overwrite:
        zip_path.unlink()

    if not zip_path.exists():
        _download(url=url, target=zip_path)
    else:
        print(f"Archive already present at {zip_path}. Skipping download.")

    expected_dir = destination.parent / EXPECTED_TOP_LEVEL_DIR

    if destination.exists():
        if overwrite:
            shutil.rmtree(destination)
        else:
            print(
                f"Destination {destination} already exists. "
                "Run with --overwrite to replace it."
            )
            return

    if expected_dir.exists() and expected_dir != destination:
        if overwrite:
            shutil.rmtree(expected_dir)
        else:
            raise FileExistsError(
                f"{expected_dir} already exists. Run with --overwrite to replace it."
            )

    _extract(zip_path=zip_path, destination_parent=destination.parent)

    if expected_dir.exists() and expected_dir != destination:
        shutil.move(str(expected_dir), str(destination))


if __name__ == "__main__":
    import tyro

    tyro.cli(main)
