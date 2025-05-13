import os
from PIL import Image
from pathlib import Path

INPUT_DIR = Path("data/raw/hindi/")
OUTPUT_DIR = Path("data/processed/hindi/")
IMAGE_SIZE = (64, 64)
VALID_EXTENSIONS = [".jpg", ".png", ".bmp", ".tiff", ".jpeg"]

def preprocess_image(input_path, output_path):
    try:
        image = Image.open(input_path).convert("L")  # Convert to grayscale
        image = image.resize(IMAGE_SIZE)            # Resize
        image.save(output_path)                     # Save to output
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for label_dir in INPUT_DIR.iterdir():
        if label_dir.is_dir():
            output_label_dir = OUTPUT_DIR / label_dir.name
            output_label_dir.mkdir(parents=True, exist_ok=True)
            
            for img_file in label_dir.glob("*"):
                if img_file.suffix.lower() in VALID_EXTENSIONS:
                    out_path = output_label_dir / (img_file.stem + ".png")
                    preprocess_image(img_file, out_path)

if __name__ == "__main__":
    run()
