from PIL import Image, ImageDraw

def draw_bounding_box(image_path, bounding_box, output_path=None):
    """
    Draws a bounding box on an image.

    image_path: Path to the input image
    bounding_box: Tuple (x_min, y_min, x_max, y_max)
    output_path: Path to save the output image (optional)
    """
    # Open the image
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    # Draw the bounding box
    draw.rectangle(bounding_box, outline="red", width=3)
    
    # Show the image
    img.show()
    
    # Save if output path is provided
    if output_path:
        print(f"Saving image with bounding box to {output_path}")
        img.save(output_path)


# Example usage
folder_path = f""
image_path = folder_path + "example_img.png"
bounding_box = (600, 300, 1200, 1000)  # Example bounding box (x_min, y_min, x_max, y_max)
output_path = "output.png"

draw_bounding_box(image_path, bounding_box, output_path)
