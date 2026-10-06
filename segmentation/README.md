# Using segmentation for querying a video

Panoptic image segmentation can be used to "query" a video. That is, by running segmentation on the frames of the video and keeping track of the found objects per frame, questions such as: 'are there any trucks in the footage, and if so, where?' can be answered. 

This is done in 3 steps: 

**1. Finding objects using segmentation**

The `segmentation_inference.py` is adapted from the segmentation model provided by NHL (see below for additional info), to also return masks. These masks is then used in `1_get_objects_per_frame.py`, to get the bounding boxes of each desired object-type detected in the frame. This is stored in a .jsonl file. The file `objects.json`, based on the mapillary labels, is used as reference list. 

Note that `1_get_objects_per_frame.py` runs the image segmentation on a folder of frames, which can - depending on the number of files etc - be time consuming. It therefore has a fallback, so that if the process gets interrupted, it will resume processing only the remaining frames. 

**2. Querying the found objects**

In `2_query_objects_per_frame.py` the results of step 1 are matched to a query as defined by the user in a query file (see `example_queries.csv`). For example, the user could look specifically for cars, or could only be interested in a specific region of the pictures. The latter can be specified by giving a bounding box. See the folder `bounding_box_selection` for tools on determining this bounding box. 

The results are stored in a dataframe (with the frames as rows, the queries as columns, counts as the values), saved to a .csv file. 

**3. Visualizing the results**  

In the notebook `3_visualize_counts_per_frame.ipynb` the results of step 2 are visualized in interactive plots, so that one can see where in a video what was found. 


**Note:** This workflow is meant to be accompanied by a user interface. 



# More on Semantic Segmentation Inference

The script <code>segmentation_inference.py</code> performs semantic segmentation masks on an image, offering options for visualization and two (semantic and panoptic) segmentation modes.
You can specify paths for input and output files, export the legend.

### Argument Options

The script uses an argument parser. Below is a breakdown of available options:

#### File Paths
- `-i`, `--input_path` (required): Path to the input image file for processing.
- `-o`, `--output_path` (required): Path to a folder to save the output image after processing.

#### Visualization
- `-v`, `--visualize`: Enable this flag to visualize the image after processing. No additional argument is required.

#### Legend
- `-l`, `--legend`: Specify a path to a legend file to export legends.

#### Segmentation Modes
- `-s`, `--semantic`: Enable this flag to use semantic segmentation mode.
- `-p`, `--panoptic`: Enable this flag to use panoptic segmentation mode.

### Example Usage

```bash
python segmentation_inference.py --input_path 'example_img/0icaMxV8_mJ8sb892WlhXA.jpg' --semantic --panoptic -v --output_path output
