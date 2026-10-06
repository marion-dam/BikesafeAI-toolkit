import argparse
import torch
from PIL import Image
from matplotlib import pyplot as plt
from mapillary_labels import plot_semantic_legend
import matplotlib.pyplot as plt
import os
import numpy as np

from mask2former_model import load_models, semantic_colormap_local

def get_segment_to_category_mapping(segments_info):
    category_mapping = {}
    for segment in segments_info:
        category_mapping[segment['id']] = segment['label_id']
    return category_mapping


def fuse_instances(result):
    category_mapping = get_segment_to_category_mapping(result['segments_info'])
    # Replace IDs with values according to the dictionary
    category_mask = result['segmentation'].clone()

    original_mask = category_mask.clone()
    for segment_id, category_id in category_mapping.items():
        category_mask[original_mask == segment_id] = category_id

    return category_mask

def panoptic_segmentation_mask(input_path, output_path, visualize: bool = False, verbose: bool = False):

    processor, model = load_models("facebook/mask2former-swin-large-mapillary-vistas-panoptic",
                                   "facebook/mask2former-swin-large-mapillary-vistas-panoptic")

    image = Image.open(input_path)
    if visualize:
        plt.figure()
        plt.imshow(image)
        plt.axis('off')
        plt.title('Original')

    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    result = processor.post_process_panoptic_segmentation(
        outputs,
        target_sizes=[image.size[::-1]]
    )[0]

    # Instance level
    instance_mask = result["segmentation"]
    
    colormap = plt.get_cmap('hsv', torch.max(instance_mask))
    colored_mask = colormap(instance_mask)

    colored_mask_image = numpy_to_pil(colored_mask[:,:,:3])

    if output_path == None or not os.path.exists(output_path):
        os.makedirs(os.path.join(os.path.dirname(input_path), 'processed'), exist_ok=True)
        output_path = os.path.join(os.path.dirname(input_path), 'processed', os.path.basename(input_path))
    else:
        output_path = os.path.join(output_path, os.path.basename(input_path))

    output_path_panoptic = add_to_filepath(output_path, 'panoptic-colored-mask')
    colored_mask_image.save(output_path_panoptic)

    if visualize:
        plt.figure()
        plt.imshow(colored_mask)
        plt.axis('off')
        plt.title('Instance level')

    # Fused categories
    category_mask = fuse_instances(result)   # note: this line changes instance_mask, shallow copy!
    colormap = semantic_colormap_local()
    #colored_mask_fused = colormap[instance_mask]
    colored_mask_fused = colormap[category_mask]

    colored_mask_fused_image = numpy_to_pil(colored_mask_fused)

    output_path_fused_panoptic = add_to_filepath(output_path, 'panoptic-fused-colored-mask')
    colored_mask_fused_image.save(output_path_fused_panoptic)

    if visualize:
        plt.figure()
        plt.imshow(colored_mask_fused)
        plt.axis('off')
        plt.title('Fused')
        plt.show()

    return output_path_panoptic, output_path_fused_panoptic, instance_mask, colored_mask_fused

def add_to_filepath(filepath: str, to_add: str):
    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)
    return os.path.join(directory, f"{name}_{to_add}{ext}")

def process_image(input_path, output_path=None, visualize: bool = False, semantic: bool = False, panoptic: bool = False):
    res_dict = {}
    # Check if input path exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"The input file {input_path} does not exist.")

    if semantic:
        file, colored_mask = semantic_segmentation_mask(input_path, output_path, visualize)
        #print(f"Semantic output saved to: {file}")
        res_dict['semantic_colored_mask'] = colored_mask


    if panoptic:
        file1, file2, instance_mask, colored_mask_fused = panoptic_segmentation_mask(input_path, output_path, visualize)
        #print(f"Panoptic output saved to: {file1, file2}")
        res_dict['panoptic_instance_mask'] = instance_mask
        res_dict['panoptic_fused_mask'] = colored_mask_fused

    return res_dict 

def numpy_to_pil(image_numpy):
    normalized_image = (image_numpy - image_numpy.min()) / (image_numpy.max() - image_numpy.min()) * 255

    colored_mask_uint8 = normalized_image.astype(np.uint8)

    # Convert NumPy array to Pillow Image
    return Image.fromarray(colored_mask_uint8)


def semantic_segmentation_mask(input_path, output_path, visualize: bool = False, verbose: bool = False):
    processor, model = load_models("facebook/mask2former-swin-large-mapillary-vistas-semantic",
                                   "facebook/mask2former-swin-large-mapillary-vistas-semantic")

    image = Image.open(input_path)

    if visualize:
        plt.figure()
        plt.title('Original')
        plt.imshow(image)
        plt.axis('off')

    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    # you can pass them to processor for postprocessing
    predicted_semantic_map = processor.post_process_semantic_segmentation(outputs, target_sizes=[image.size[::-1]])[0]

    # Map labels to RGB values
    colormap = semantic_colormap_local()
    colored_mask = colormap[predicted_semantic_map]

    if verbose:
        print(f"Save output to {output_path}")

    colored_mask_image = numpy_to_pil(colored_mask)
    if output_path == None or not os.path.exists(output_path):
        os.makedirs(os.path.join(os.path.dirname(input_path), 'processed'), exist_ok=True)
        output_path_semantic = os.path.join(os.path.dirname(input_path), 'processed', os.path.basename(input_path))
    else:
        output_path_semantic = os.path.join(output_path, os.path.basename(input_path))
    output_path_semantic = add_to_filepath(output_path_semantic, 'colored-mask')
    colored_mask_image.save(output_path_semantic)

    if visualize:
        # Plot the segmentation mask
        plt.figure()
        plt.title('Colored Mask')
        plt.imshow(colored_mask)
        plt.axis('off')
        plt.show()

    return output_path_semantic, colored_mask

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Semantic segmentation mask converter")

    # Group for input and output paths
    path_group = parser.add_argument_group("File Paths")
    path_group.add_argument("-i", "--input_path", required=True, type=str, help="Path to the input image file")
    path_group.add_argument("-o", "--output_path", required=True, type=str, help="Path to a folder to save the output image")

    # Group for visualization option
    viz_group = parser.add_argument_group("Visualization")
    viz_group.add_argument("-v", "--visualize", action="store_true", help="Enable visualization of the image")

    # Group for legend option
    legend_group = parser.add_argument_group("Legend")
    legend_group.add_argument("-l", "--legend", type=str, help="Give a path to open the legend")

    # Group for segmentation option
    segmentation_mode_group = parser.add_argument_group("Segmentation Mode")
    segmentation_mode_group.add_argument("-s", "--semantic", action="store_true",
                                         help="Enable to semantic segmentation")
    segmentation_mode_group.add_argument("-p", "--panoptic", action="store_true",)

    # Parse arguments
    args = parser.parse_args()

    if args.output_path != None and not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    # Call the image processing function
    process_image(args.input_path, args.output_path, args.visualize, args.semantic, args.panoptic)

    plot_semantic_legend(config_path=args.legend, visualize=args.visualize, output_path=args.output_path)
