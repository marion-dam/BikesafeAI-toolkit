# BikeSafeAI: Toolkit for Footage Selection

This repository contains code developed by Hanze as part of the **BikeSafeAI project**, focusing on selecting relevant moments from video footage collected for traffic safety analysis.  

For the related AI tools that analyze traffic safety indicators, see the [Traffic Safety GitHub](https://github.com/imaihub/traffic-safety) by **imaihub/NHL Stenden**.


## Purpose
The main functionality currently here is **footage selection**—methods to reduce the amount of raw video by identifying segments that are most relevant for analysis. Two approaches are provided, as well as a folder containing basic functionality when working with videos:


### 1. Using Image Segmentation to “Query” a Video
**Folder:** `segmentation`  
Using segmentation, the occurence of specific objects in each frame is counted. This enables querying the video (e.g., “Which frames contain traffic lights/trucks/etc?”) and creating visualizations to identify and select potentially interesting moments. 

This is suitable for video footage from a fixed camera (i.e, a camera that is always focused on the same traffic situation), as well as for video footage from a camera mounted on a bicycle.

*Note:* In a similar way, [anomaly detection](https://github.com/imaihub/traffic-safety-anomaly-detection) can be applied to focus on unusual or potentially interesting moments.



### 2. Using GPS and Other Data Sources to Identify Specific Situations
**Folder:** `gps_and_nwb`  
- Contains two notebooks demonstrating how GPS data linked to a video can be used to select segments based on location, speed, or road characteristics from the **Nationaal Wegenbestand (NWB)**.  
- Assumes GPS data has been extracted from the video and stored in a `.gpx` file (instructions in readme).  

This is suitable for video footage from a camera mounted on a bicycle that also collects GPS (such as a GoPro).



### 3. Basic Video Editing
**Folder:** `basic_video_editing`  
- Provides utilities for handling long videos:
  - Create subclips from larger videos.
  - Convert videos into folders of frames (required for AI models).
  - Recombine frames back into video format.  
- Includes scripts and examples for:
  - Splitting videos into segments.
  - Extracting frames at intervals.
  - Converting frames back to video.


---








