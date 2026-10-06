import cv2
import os
import argparse

def frames_to_video(input_folder, output_file, fps):
    """
    Converts a sequence of image frames from a specified folder into a video file.
    Args:
        input_folder (str): Path to the folder containing the image frames. 
                            The frames should be in .png, .jpg, or .jpeg format.
        output_file (str): Path to the output video file, including the file name and extension (e.g., .mp4).
        fps (int): Frames per second for the output video.
    Raises:
        ValueError: If no image frames are found in the input folder.
    Notes:
        - The function assumes that the image frames are named in a way that allows sorting 
          (e.g., frame1.jpg, frame2.jpg, ...).
        - The video dimensions are determined based on the first image frame in the folder.
    """

    # Get all frame file names and sort them
    frames = sorted([f for f in os.listdir(input_folder) if f.endswith(('.png', '.jpg', '.jpeg'))])
    if not frames:
        raise ValueError("No image frames found in the input folder.")

    # Read the first frame to get video dimensions
    first_frame_path = os.path.join(input_folder, frames[0])
    first_frame = cv2.imread(first_frame_path)
    height, width, _ = first_frame.shape

    # Define the video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 files
    video_writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    # Write each frame to the video
    for frame_name in frames:
        frame_path = os.path.join(input_folder, frame_name)
        frame = cv2.imread(frame_path)
        video_writer.write(frame)

    video_writer.release()
    print(f"Video saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a folder of frames into a video.")
    parser.add_argument("--input_folder", type=str, help="Path to the folder containing frames.")
    parser.add_argument("--output_video", type=str, help="Path to save the output video file.")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second for the output video (default: 30).")

    args = parser.parse_args()

    try:
        frames_to_video(args.input_folder, args.output_video, args.fps)
    except Exception as e:
        print(f"Error: {e}")