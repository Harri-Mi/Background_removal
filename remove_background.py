import os
from rembg import remove
from PIL import Image

input_folder = 'Input_images'  # Your folder with images with white background
output_folder = 'Output_images'  # Folder where images without background will be saved

os.makedirs(output_folder, exist_ok=True)

image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
total_images = len(image_files)

for index, filename in enumerate(image_files):
    print(f"Processing image {index + 1}/{total_images}: {filename}")
    input_path = os.path.join(input_folder, filename)
    output_path = os.path.join(output_folder, filename)
    
    with open(input_path, 'rb') as i:
        input_data = i.read()
        output_data = remove(input_data)

    with open(output_path, 'wb') as o:
        o.write(output_data)

print(f'\nAll {total_images} images processed and saved to {output_folder}')
