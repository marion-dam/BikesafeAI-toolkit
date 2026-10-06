def pick_backend():
    """Try TkAgg for interactivity; fall back to Agg if not available."""
    import matplotlib
    try:
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt  # noqa: F401
        return "TkAgg"
    except Exception:
        matplotlib.use("Agg")
        return "Agg"

backend = pick_backend()
print(f"Using backend: {backend}")


import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import matplotlib.patches as patches
from PIL import Image

# Global variable to store selected bounding box
selected_bbox = None

def onselect(eclick, erelease):
    """
    Callback when user selects a region.
    """
    global selected_bbox
    x1, y1 = int(eclick.xdata), int(eclick.ydata)
    x2, y2 = int(erelease.xdata), int(erelease.ydata)

    # Ensure consistent ordering (xmin, ymin, xmax, ymax)
    x_min, x_max = sorted([x1, x2])
    y_min, y_max = sorted([y1, y2])

    selected_bbox = (x_min, y_min, x_max, y_max)
    print("Selected bounding box:", selected_bbox)


def select_bounding_box(image_path):
    """
    Opens an image and lets the user select a bounding box interactively.
    """
    global ax

    img = Image.open(image_path)
    fig, ax = plt.subplots(1)
    ax.imshow(img)

    toggle_selector = RectangleSelector(
        ax, onselect,
        useblit=True,
        button=[1],  # left click
        minspanx=5, minspany=5,
        spancoords='pixels',
        interactive=True
    )

    plt.show()
    return selected_bbox


# Example usage
folder_path = ""
image_path = folder_path + "example_img.png"

bbox = select_bounding_box(image_path)
print("Final bounding box (xmin, ymin, xmax, ymax):", bbox)
