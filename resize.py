from PIL import Image
import os
from multiprocessing import Pool, cpu_count

# 输入和输出文件夹路径
input_folder = "/Users/zz/codes/TimeLapseCam/frames"

target_size = (1920, 1080)  # 目标分辨率

# 获取文件列表并按字母顺序排序
file_list = sorted([f for f in os.listdir(input_folder) if f.endswith(".png")])

# 定义处理函数
def process_image(filename):
    image_path = os.path.join(input_folder, filename)
    img = Image.open(image_path)
    if img.size == target_size:
        print(f"Skipped (already correct size): {filename}")
        return
    img_resized = img.resize(target_size, Image.LANCZOS)
    img_resized.save(image_path)
    print(f"Resized: {filename}")

# 使用多进程处理
if __name__ == "__main__":
    max_files = 1000
    file_list = file_list[:max_files]
    
    with Pool(cpu_count()) as pool:
        pool.map(process_image, file_list)
