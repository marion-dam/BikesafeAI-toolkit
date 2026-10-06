# Basic Video Editing

Utilities and examples for quick, scriptable video tasks:

- **Create subclips** from a larger video.
- **Extract frames** at a chosen interval.
- **Recombine frames** back into a video.
- Shell helpers to **batch split** videos into equal-length segments.

This folder includes:

- `video_editing.py` — To show video specs, create subclip, extract frames and/or split video into segments
- `frames_to_video.py` — To convert a folder of images to a video.

Examples (shell scripts and python): 
- `create_segments.sh` — Split a video into fixed-length segments using `ffmpeg`.
- `create_subclip_and_frames.sh` — Create a subclip and extract frames in one go.
- `example_call_create_subclip_and_frames.py` — Python example calling utilities from `basic_video_editing.video_editing`.


---

## Requirement: ffmpeg

To check ffmpeg
```bash
ffmpeg -version
```
If this prints a version, you're good. If not, install ffmpeg:
- Ubuntu/WSL: `sudo apt-get update && sudo apt-get install -y ffmpeg`
- macOS (Homebrew): `brew install ffmpeg`
- Windows: Install from https://ffmpeg.org/ and add the `bin` folder to PATH.

---

## Generic Command Templates

**Split video into segments**
```bash
python create_subclip_and_frames.py \
  --video "/path/to/input_video.mp4" \
  --split_segments \
  --segment_length 30 \
  --output_segments "/path/to/output_video_segments/"
```

**Select segment of a video**

```bash
python create_subclip_and_frames.py \
--video "/path/to/input_video.MP4" \
--start "00:03:00" \
--end "00:04:00" \
--output_video "/path/to/output_video.MP4" \ 
```

**Convert frames to video**
```bash
python frames_to_video.py \
  --input_folder "/path/to/frames" \
  --output_video "/path/to/output_video.mp4" \
  --fps 30
```


**Notes**
- Segment length is in seconds.
- Output directory will be created if it does not exist.
- Filenames typically follow `segment_0001.mp4`, `segment_0002.mp4`, ...


