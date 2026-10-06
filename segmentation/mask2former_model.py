from transformers import AutoImageProcessor, Mask2FormerForUniversalSegmentation
from mapillary_labels import semantic_colormap

def load_models(processor_type, model_type):

    # load Mask2Former fine-tuned on Mapillary Vistas panoptic segmentation
    processor = AutoImageProcessor.from_pretrained(processor_type)
    model = Mask2FormerForUniversalSegmentation.from_pretrained(model_type)

    return processor, model

def semantic_colormap_local():
    return semantic_colormap()