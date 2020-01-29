Fast Scene Detection
--------------------

HD videos are large files that contain a huge amount of information. However, a video can be summarized by extracting
the scenes that comprise it. This tool attempts to extract scenes quickly from an input video.


Installation
------------

Make a virtualenv and install the dependencies by running the following 3 commands:

```python3
virtualenv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```


Usage
-----

General:

```
usage: main.py [-h] [--source_path SOURCE_PATH] [--save_path SAVE_PATH]
               [--library_path LIBRARY_PATH] [--visualize_scenes]            
```

Available options:

| Argument            | Values                                       | Purpose                                            |
|---------------------|----------------------------------------------|----------------------------------------------------|
|`--source_path`      | "path/to/video.mp4", "path/to/video_folder"  | A video source file or directory containing videos |        
|`--save_path`        | "path/to/save/to"                            | A path to save a pickled segmented video object    |
|`--library_path`     | "path/to/pickled/video_collection"           | A path to a saved segmented video pickle object    |
|`--visualize_scenes` | None                                         | Whether or not to visualize scenes                 |


FAQs
---

1. #### What is this?

    It's a small package that attempts to divide a video into scenes based on its content. You give it a video and it
gives you a list of timestamps where each scene strats. It also lets you visualize and save extracted scenes.

2. #### How does it work?

   It works by taking the perceptual hashes (pHash) of input video frames.
If the perceptual hash difference of consecutive frames is large (i.e. their Hamming distance), then this is considered
a scene change. The top N biggest hash differences are returned and are considered to be the "scenes" of the video.

3. #### What makes it fast?

   Higher speed is achieved by reducing scene search granularity: i.e. not all frames are hashed. For a video with 100,000 
frames, this tool would hash 1 out of every ~430 frames. If the video is 60 FPS, then that means a scene change is 
checked for roughly every ~7 seconds. The trade-off between search granularity and speed is controllable via command 
line parameters.

4. #### Aren't there tools that already do this kind of thing?

   There is a great library called PySceneDetect that is commonly used for scene detection. It works great but it seemed a
little slow for longer videos so I threw this script together quickly. I highly recommend PySceneDetect, though! 

5. #### Is this method even a good way to extract scenes from a video?

   Truthfully, I can't give you an objective answer, but I think it's okay based on my subjective experience. 
However, for all I know, it could be horrible compared to other methods! If someone runs the results through an 
objective metric of scene detection, tell me how this script does compared to other things. This is purely experimental,
so use at your own discretion.

6. #### What are the limitations?

   Within the results, there are times when 2 or more consecutive scenes look too similar. I suspect this happens 
because the perceptual hashes of the frames are sufficiently different to appear in the results, but don't necessarily 
qualify for what a human might call two different scenes.

   Also, fade transitions, where two or more frames slowly blend into one another, could give this algorithm a very hard
time. Transition effects are problematic because the Hamming distance of perceptual hashes of blended frames can be
low, and therefore may not register as a scene change. 


Sample Visualization 
--------------------

![](https://i.imgur.com/R1ZNw1p.jpg)
