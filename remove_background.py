import os
from rembg import remove
from PIL import Image

input_folder = 'Input_images'  # Your folder with images with white background
output_folder = 'Output_images'  # Folder where images without background will be saved

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        with open(input_path, 'rb') as i:
            input_data = i.read()
            output_data = remove(input_data)

        with open(output_path, 'wb') as o:
            o.write(output_data)

print(f'Processed images saved to {output_folder}')
