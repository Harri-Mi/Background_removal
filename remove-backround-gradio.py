import gradio as gr
import os
from rembg import remove
from PIL import Image
import io
import zipfile
from typing import List, Tuple

def remove_background_single(image_file) -> Image.Image:
    """Remove background from a single image file"""
    if image_file is None:
        return None
    
    # Read the image data
    if hasattr(image_file, 'read'):
        input_data = image_file.read()
    else:
        with open(image_file, 'rb') as f:
            input_data = f.read()
    
    # Remove background
    output_data = remove(input_data)
    
    # Convert to PIL Image
    output_image = Image.open(io.BytesIO(output_data))
    return output_image

def remove_background_multiple(image_files) -> Tuple[str, List[Image.Image]]:
    """Remove background from multiple image files and return as zip + preview images"""
    if not image_files:
        return None, []
    
    processed_images = []
    preview_images = []
    
    # Create a zip file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, image_file in enumerate(image_files):
            try:
                # Get original filename or create one
                if hasattr(image_file, 'name') and image_file.name:
                    original_name = os.path.basename(image_file.name)
                    name_without_ext = os.path.splitext(original_name)[0]
                else:
                    name_without_ext = f"image_{i+1}"
                
                # Remove background
                processed_image = remove_background_single(image_file)
                
                if processed_image:
                    # Save to zip file
                    img_buffer = io.BytesIO()
                    processed_image.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    zip_file.writestr(f"{name_without_ext}_no_bg.png", img_buffer.getvalue())
                    
                    # Add to preview (limit to first 5 images for display)
                    if len(preview_images) < 5:
                        preview_images.append(processed_image)
                    
            except Exception as e:
                print(f"Error processing image {i+1}: {str(e)}")
                continue
    
    zip_buffer.seek(0)
    
    # Save zip file temporarily
    zip_path = "processed_images.zip"
    with open(zip_path, 'wb') as f:
        f.write(zip_buffer.getvalue())
    
    return zip_path, preview_images

def process_images(single_image, multiple_images, processing_mode):
    """Main processing function based on selected mode"""
    if processing_mode == "Single Image":
        if single_image is None:
            return None, None, None, "Please upload an image first."
        
        try:
            result = remove_background_single(single_image)
            return result, None, None, "Background removed successfully!"
        except Exception as e:
            return None, None, None, f"Error processing image: {str(e)}"
    
    else:  # Multiple Images
        if not multiple_images:
            return None, None, None, "Please upload at least one image."
        
        try:
            zip_file, preview_images = remove_background_multiple(multiple_images)
            if zip_file and preview_images:
                return None, preview_images, zip_file, f"Processed {len(multiple_images)} images successfully! Download the zip file to get all results."
            else:
                return None, None, None, "No images were processed successfully."
        except Exception as e:
            return None, None, None, f"Error processing images: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Background Removal Tool", theme=gr.themes.Default()) as app:
    gr.Markdown(
        """
        # 🖼️ Background Removal Tool
        
        Upload your images and get them back with transparent backgrounds!
        
        **Choose your mode:**
        - **Single Image**: Upload one image and preview the result
        - **Multiple Images**: Upload multiple images and download them as a zip file
        """
    )
    
    with gr.Row():
        processing_mode = gr.Radio(
            choices=["Single Image", "Multiple Images"],
            value="Single Image",
            label="Processing Mode"
        )
    
    with gr.Row():
        with gr.Column():
            # Single image input (visible by default)
            single_image_input = gr.File(
                label="Upload Single Image",
                file_types=["image"],
                visible=True
            )
            
            # Multiple images input (hidden by default)
            multiple_images_input = gr.File(
                label="Upload Multiple Images",
                file_count="multiple",
                file_types=["image"],
                visible=False
            )
            
            process_btn = gr.Button("Remove Background", variant="primary", size="lg")
        
        with gr.Column():
            # Output for single image
            single_output = gr.Image(
                label="Result",
                visible=True
            )
            
            # Output for multiple images
            multiple_output_gallery = gr.Gallery(
                label="Preview (first 5 images)",
                visible=False,
                columns=3,
                rows=2,
                height="auto"
            )
            
            download_file = gr.File(
                label="Download All Processed Images",
                visible=False
            )
    
    status_message = gr.Textbox(label="Status", interactive=False)
    
    # Function to toggle visibility based on mode
    def toggle_inputs(mode):
        if mode == "Single Image":
            return (
                gr.update(visible=True),   # single_image_input
                gr.update(visible=False),  # multiple_images_input
                gr.update(visible=True),   # single_output
                gr.update(visible=False),  # multiple_output_gallery
                gr.update(visible=False)   # download_file
            )
        else:
            return (
                gr.update(visible=False),  # single_image_input
                gr.update(visible=True),   # multiple_images_input
                gr.update(visible=False),  # single_output
                gr.update(visible=True),   # multiple_output_gallery
                gr.update(visible=True)    # download_file
            )
    
    # Toggle inputs when mode changes
    processing_mode.change(
        fn=toggle_inputs,
        inputs=[processing_mode],
        outputs=[single_image_input, multiple_images_input, single_output, multiple_output_gallery, download_file]
    )
    
    # Process images when button is clicked
    process_btn.click(
        fn=process_images,
        inputs=[single_image_input, multiple_images_input, processing_mode],
        outputs=[single_output, multiple_output_gallery, download_file, status_message]
    )
    
    # Remove the separate gallery update function since we're handling it directly now

    gr.Markdown(
        """
        ### 📝 Instructions:
        1. Choose your processing mode (Single or Multiple images)
        2. Upload your image(s) - supports PNG, JPG, JPEG formats
        3. Click "Remove Background" to process
        4. For single images: preview the result directly
        5. For multiple images: download the zip file containing all processed images
        
        ### ⚡ Features:
        - Automatic background removal using AI
        - Support for batch processing
        - Transparent PNG output
        - Easy download of results
        """
    )

if __name__ == "__main__":
    app.launch(share=True)