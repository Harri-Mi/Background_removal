import gradio as gr
from rembg import remove
from PIL import Image
import io

def remove_background(image: Image.Image) -> Image.Image:
    # Convert PIL image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    input_data = img_byte_arr.getvalue()
    
    # Remove background
    output_data = remove(input_data)
    
    # Convert bytes back to PIL image
    output_img = Image.open(io.BytesIO(output_data)).convert("RGBA")
    return output_img

iface = gr.Interface(
    fn=remove_background,
    inputs=gr.Image(type="pil"),
    outputs=gr.Image(type="pil"),
    title="Background Remover",
    description="Upload an image and remove its background automatically."
)

iface.launch()
