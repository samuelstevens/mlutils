# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "beartype",
#     "tqdm",
#     "tyro",
# ]
# ///

# convert_to_imagefolder.py
"""
Converts the original CUB_200_2011 dataset into a typical ImageFolder format on disk:

CUB_200_2011_ImageFolder/
    train/
        001.Black_footed_Albatross/
            Black_Footed_Albatross_0001_796111.jpg
            ...
        ...
        200.Common_Yellowthroat/
            Common_Yellowthroat_0003_190521.jpg
            ...
    test/

        001.Black_footed_Albatross/
            ...
        ...
        200.Common_Yellowthroat/
            ...

Run this script with

uv run convert_to_imagefolder.py
"""

import pathlib
import shutil

import beartype
import tqdm


@beartype.beartype
def main(
    orig: pathlib.Path = pathlib.Path(".", "CUB_200_2011"),
    out: pathlib.Path = pathlib.Path(".", "CUB_200_2011_ImageFolder"),
):
    """Entry point.

    Args:
        orig: Path to original CUB dataset with images.txt, train_test_split.txt, etc.
    """
    img_id_to_path = {}
    with open(orig / "images.txt") as fd:
        for line in fd:
            img_id, path = line.split()
            img_id_to_path[int(img_id)] = pathlib.Path(path)

    img_id_to_split = {}
    with open(orig / "train_test_split.txt") as fd:
        for line in fd:
            img_id, is_train = line.split()
            img_id_to_split[int(img_id)] = "train" if is_train == "1" else "test"

    cls_id_to_cls_name = {}
    with open(orig / "classes.txt") as fd:
        for line in fd:
            cls_id, cls_name = line.split()
            cls_id_to_cls_name[int(cls_id)] = cls_name

    img_id_to_cls_name = {}
    with open(orig / "image_class_labels.txt") as fd:
        for line in fd:
            img_id, cls_id = line.split()
            img_id_to_cls_name[int(img_id)] = cls_id_to_cls_name[int(cls_id)]

    for img_id, img_path in tqdm.tqdm(img_id_to_path.items()):
        split = img_id_to_split[img_id]
        cls = img_id_to_cls_name[img_id]
        (out / split / cls).mkdir(parents=True, exist_ok=True)
        shutil.copy2(orig / "images" / img_path, out / split / cls / img_path.name)


if __name__ == "__main__":
    import tyro

    tyro.cli(main)
