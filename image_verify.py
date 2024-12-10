from PIL import Image
import os

input_folder = "/Users/zz/codes/TimeLapseCam/frames"

for filename in os.listdir(input_folder):
    if filename.endswith(".png"):
        image_path = os.path.join(input_folder, filename)
        try:
            with Image.open(image_path) as img:
                img.verify()
        except Exception:
            print(f"Corrupted: {filename}")
            os.remove(image_path)
            print(f"Removed: {filename}")
