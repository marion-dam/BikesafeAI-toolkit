from moviepy.editor import VideoFileClip
from PIL import Image
from pathlib import Path
import argparse
import sys


def show_video_specs(video_path):
    """
    Displays the specifications of a video file, including duration, FPS, and resolution.
    Args:
        video_path (str): The path to the input video file.
    Returns:
        None
    """
    video = VideoFileClip(video_path)
    print(f"Video duration: {video.duration} seconds")
    print(f"Video FPS: {video.fps}")
    print(f"Video resolution: {video.size}")
    video.close()


def create_subclip(video_path, start_time, end_time, output_video_path, compress_height = None):
    """
    Extracts a subclip from a video file, removes its audio, and saves it as a new video file.
    Args:
        video_path (str): The path to the input video file.
        start_time (str): The start time of the subclip as a string "HH:MM:SS".
        end_time (str): The end time of the subclip as a string "HH:MM:SS".
        output_video_path (str): The path to save the output video file.
    Returns:
        None
    """
    video = VideoFileClip(video_path)

    # Cut selected clip
    cut_clip = video.subclip(start_time, end_time)
    cut_clip = cut_clip.without_audio()

    if compress_height:
        cut_clip = cut_clip.resize(height=compress_height)  

    # Save the cut clip as a new file
    cut_clip.write_videofile(output_video_path, codec="libx264")
    video.close()


def extract_frames(video_path, output_folder, save_every_nth, prefix = ''):
    """
    Extracts frames from a video file and saves them as image files.
    Args:
        video_path (str): The path to the input video file.
        output_folder (str): The folder where the extracted frames will be saved.
        save_every_nth (int): The interval for saving frames. For example, if set to 5, 
                              every 5th frame will be saved.
    Returns:
        None
    Raises:
        FileNotFoundError: If the video file does not exist.
        ValueError: If save_every_nth is less than or equal to 0.
    Notes:
        - The frames are saved in PNG format with filenames in the format "{output_folder}{i}.png".
    """

    video_clip = VideoFileClip(video_path)

    # Iterate over all frames
    i = 0
    for frame in video_clip.iter_frames(fps=video_clip.fps, dtype="uint8"):
        if i % save_every_nth == 0:
            image = Image.fromarray(frame)
            output_path = f"{output_folder}{prefix}{i}.png"
            image.save(output_path)
        i += 1
    video_clip.close()
    print(f'Frames saved in {output_folder}')
    

def split_video_into_segments(video_path, segment_length, output_folder, compress_height = None):
    """
    Splits a video into smaller segments of fixed length, remove audio and saves them as separate video files.
    Args:
        video_path (str): The path to the input video file.
        segment_length (int): The length of each segment in seconds.
        output_folder (str): The folder where the video segments will be saved.
    Returns:
        None
    Raises:
        FileNotFoundError: If the video file does not exist.
        ValueError: If segment_length is less than or equal to 0.
    """
    if segment_length <= 0:
        raise ValueError("Segment length must be greater than 0.")

    video = VideoFileClip(video_path)
    total_duration = int(video.duration)
    output_folder_path = Path(output_folder)
    output_folder_path.mkdir(parents=True, exist_ok=True)

    for start_time in range(0, total_duration, segment_length):
        end_time = min(start_time + segment_length, total_duration)
        segment = video.subclip(start_time, end_time)
        segment = segment.without_audio() 
        if compress_height:
            
            segment = segment.resize(height=compress_height)  
        output_path = output_folder_path / f"segment_{start_time}_{end_time}.mp4"
        segment.write_videofile(str(output_path), codec="libx264")
        segment.close()

    video.close()
    print(f'Video segments stored in {output_folder}')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video processing: extract a segment, video to frames, or separate long video into segments of fixed length (with optional compression). NOTE: if both create_subclip and extract_frames are set, \nthe subclip will be used for frame extraction.")
    parser.add_argument("--show_video_specs", action="store_true", help="Show video specs")	
    parser.add_argument("--video", required=True, help="Path to the input video file")
    parser.add_argument("--start", help="Start time for subclip (format: HH:MM:SS)")
    parser.add_argument("--end", help="End time for subclip (format: HH:MM:SS)")
    parser.add_argument("--output_video", help="Path to save the subclip video")
    parser.add_argument("--output_frames", help="Folder to save extracted frames")
    parser.add_argument("--save_every", type=int, default=50, help="Save every N-th frame")
    parser.add_argument("--create_subclip", action="store_true", help="Flag to create a subclip")
    parser.add_argument("--extract_frames", action="store_true", help="Flag to extract frames from video")
    parser.add_argument("--split_segments", action="store_true", help="Flag to split video into segments")
    parser.add_argument("--segment_length", type=int, help="Length of each segment in seconds")
    parser.add_argument("--output_segments", help="Folder to save video segments")
    parser.add_argument("--compress_height", type=int, help="Compress segment video height to this value (optional)")
    args = parser.parse_args()

    if args.show_video_specs:
        if not Path(args.video).exists():
            parser.error(f"Video file {args.video} does not exist.")
        show_video_specs(args.video)

    if args.create_subclip:
        if not args.start or not args.end or not args.output_video:
            parser.error("--create_subclip requires --start, --end, and --output_video")
        create_subclip(args.video, args.start, args.end, args.output_video)

    if args.extract_frames:
        if not args.output_frames:
            parser.error("--extract_frames requires --output_frames")
        folder_path = Path(args.output_frames)
        folder_path.mkdir(parents=True, exist_ok=True)
        extract_frames(args.video if not args.create_subclip else args.output_video, args.output_frames, args.save_every)

    if args.split_segments:
        if not args.segment_length or not args.output_segments:
            parser.error("--split_segments requires --segment_length and --output_segments")
        folder_path = Path(args.output_segments)
        folder_path.mkdir(parents=True, exist_ok=True)
        if args.compress_height:
            split_video_into_segments(args.video, args.segment_length, args.output_segments, args.compress_height)
        else:
            split_video_into_segments(args.video, args.segment_length, args.output_segments)






