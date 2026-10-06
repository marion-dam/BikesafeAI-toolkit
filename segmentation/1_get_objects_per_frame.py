import os
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import json

from mask2former_model import load_models, semantic_colormap_local
from segmentation_inference import process_image, numpy_to_pil


def extract_objects_from_masks(pim, pfm):
    """
    Extract instance metadata (class name, ID, bbox) from panoptic masks.
    
    :param pim: panoptic instance mask (torch.Tensor)
    :param pfm: panoptic fused mask (torch.Tensor with RGB values per pixel)
    :return: dict with instance metadata
    """
    found_objects_dict = {}

    for val in torch.unique(pim):
        val = val.item()
        if val == 0:  # background
            continue

        mask = (pim == val)
        pfm_values = pfm[mask]

        # Determine semantic class via color (first pixel is enough)
        rgb = tuple(pfm_values[0])
        class_name = COLOR_TO_NAME.get(rgb, None)

        if class_name is None:  # ignore unknown classes
            continue

        # Compute bounding box
        indices = mask.nonzero(as_tuple=False)
        min_row, min_col = indices.min(dim=0).values
        max_row, max_col = indices.max(dim=0).values
        bbox = (min_col.item(), min_row.item(), max_col.item(), max_row.item())

        # Store metadata
        found_objects_dict.setdefault(class_name, []).append({
            "id": int(val),
            "bbox": bbox
        })

    return found_objects_dict

# -------------------------
# Main processing loop
# 0. Find all frames in selected folder. Then, for each frame:
# 1. Run panoptic segmentation
# 2. Look for the objects items in the output masks
# 3. Store in jsonl (one line per frame)
# -------------------------
def segment_frames(folder_path, output_jsonl, restart = False):
    png_files = [file for file in os.listdir(folder_path) if file.endswith(".png")]

    if restart and os.path.exists(output_jsonl):
        with open(output_jsonl, "r") as f:
            processed_files = {list(json.loads(line).keys())[0] for line in f}
        png_files = [file for file in png_files if file not in processed_files]
        print(f'Restarting segmentation. {len(png_files)} frames left to process.')
        mode = "a" # append mode for opening file
    else:
        print(f'Starting segmentation for {len(png_files)} frames.')
        mode = "w" # write mode

    # counter to keep track of progress
    counter = 0

    with open(output_jsonl, mode) as f:

        for file in png_files:

            counter += 1
            if counter % 50 == 0: 
                print(f'Processed {counter} frames')

            input_path = os.path.join(folder_path, file)
            im_dict = process_image(input_path, None, False, False, True)
            pim, pfm = im_dict['panoptic_instance_mask'], im_dict['panoptic_fused_mask']
        
            found_object_dict = extract_objects_from_masks(pim, pfm)
            record = {file: found_object_dict}
            f.write(json.dumps(record) + "\n")

        return 



if __name__ == "__main__":
    # define output file and folder
    output_jsonl = 'objects_per_frame_example.jsonl'

    object_colors_file = 'objects.json'
    base_folder = "/path/to/folder_with_frames/"
    
    folder_path = base_folder 
    

    with open(object_colors_file, "r") as f:
        OBJECTS = json.load(f)

    # Reverse map: RGB → class name
    COLOR_TO_NAME = {tuple(v): k for k, v in OBJECTS.items()}

    # In case of interruption, set restart to True (prevents doing all frames again)
    restart = True

    if os.path.exists(output_jsonl) and restart == False:
        print(f'Output file {output_jsonl} already exists while restart is set to False. This means the file will be overwritten. Proceed? Y/n')
        ans = input()
        if ans.lower() == 'n':
            print('Exiting.')
            exit()

    segment_frames(folder_path, output_jsonl, restart)