from __future__ import annotations

from tensorflow.keras.preprocessing.image import ImageDataGenerator

from e5_rps_utils import SEED, ensure_dirs, prepare_dataset, project_root


IMG_SIZE = (150, 150)
BATCH_SIZE = 32


def main() -> None:
    root = project_root()
    ensure_dirs(root)
    train_dir, _, _, _ = prepare_dataset(root)
    generator = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2).flow_from_directory(
        train_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
        seed=SEED,
    )
    index_to_class = {index: name for name, index in generator.class_indices.items()}
    labels = [index_to_class[i] for i in range(len(index_to_class))]
    output = root / "models" / "labels.txt"
    output.write_text("\n".join(labels) + "\n", encoding="utf-8")
    print(f"Labels exported to {output}")
    print(labels)


if __name__ == "__main__":
    main()
