from __future__ import annotations

import pathlib

import tensorflow as tf

from e5_utils import ensure_dirs, project_root


DATASET_URL = "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz"


def main() -> None:
    root = project_root()
    ensure_dirs(root)
    data_dir = tf.keras.utils.get_file("flower_photos", origin=DATASET_URL, untar=True)
    data_path = pathlib.Path(data_dir)
    labels = sorted(item.name for item in data_path.glob("*") if item.is_dir())
    output = root / "models" / "labels.txt"
    output.write_text("\n".join(labels) + "\n", encoding="utf-8")
    print(f"Labels exported to {output}")
    print(labels)


if __name__ == "__main__":
    main()
