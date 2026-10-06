from basic_video_editing.video_editing import create_subclip, extract_frames, show_video_specs
from pathlib import Path

video = "/path/to/input_video.MP4" 
start = "00:03:00" 
end = "00:04:00" 
output_video = "/path/to/output_segments/" 
output_frames = "/path/to/output_frames/"
save_every = 1000 
creating_subclip = True 
extracting_frames = True

show_video_specs(video)

if creating_subclip:
    create_subclip(video_path=video, start_time=start, end_time=end, output_video_path=output_video)

if extracting_frames:

    folder_path = Path(output_frames)
    folder_path.mkdir(parents=True, exist_ok=True)
    extract_frames(video_path=video if not create_subclip else output_video, output_folder=output_frames, save_every_nth=save_every)
