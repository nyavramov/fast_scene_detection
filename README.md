### Motivation
HD Video files are generally large files containing a huge amount of information. It would be nice if there was a way to summarize all this information by extracting scenes that occur throughout the video. This way, we could view all of the scenes in the video at a glance.

### What is this?
It's a small script that attempts to divide a video into scenes based on its content. When run, this script provides a list of timestamps and frame numbers where each scene occurs. It also has an additional option to visualize the frame where each scene starts. 

### How does it work?
It works by using perceptual hashes (pHash) and iterating through frames of an input video, taking the perceptual hash of each frame. If the perceptual hash difference of consecutive frames is large (i.e. their Hamming distance), then this is considered a scene change. The top N biggest hash differences are returned and are considered to be the "scenes" of the video (N=40, by default, but can be changed by changing the `SCENE_LIMIT` variable).

However, not all frames are hashed. In fact, for a video with 100,000 frames, this script would hash 1 out of every ~430 frames. If the video is 60 FPS, then that means the script "checks" for a scene change roughly every ~7 seconds. This decision to skip frames is intentional because my usage prioritizes speed over quality. Furthermore, I assumed that scenes don't change very quickly. However, this behavior is adjustable by changing the `STEPSIZE_CONSTANT`.

### Aren't there tools that already do this kind of thing?
There is a great library called PySceneDetect that is commonly used for scene detection. It works great but it seemed a little slow for longer videos so I threw this script together quickly. I highly recommend PySceneDetect, though! 

### Is this method even a good way to extract scenes from a video?
Truthfully, I can't give you an objective answer, but I think it's okay based on my subjective experience. However, for all I know, it could be horrible compared to other methods! If someone runs the results through an objective metric of scene detection, tell me how this script does compared to other things. This is purely experimental, so use at your own discretion.

### Does it have any problems?
Of course! Within the results, there are times when 2 or more consecutive frames look similar. I suspect this happens because the perceptual hashes of the frames are sufficiently different to appear in the results, but don't necessarily qualify for what a human might call two different scenes.

Also, fade transitions, where two or more frames slowly blend into one another, could give this algorithm a very hard time. Transition effects are problematic because the Hamming distance of perceptual hashes of blended frames will be low, and therefore may not register as a scene change. 

### How do I use it?
First, make a virtualenv and install the dependencies by running the following 3 commands:

`virtualenv venv`

`source venv/bin/activate`

`python3 -m pip install -r requirements.txt`

Then use with:

`python3 segment_scene.py "path/to/video.mp4"`

### How do I turn off the visualization?
Just make sure the `visualize_scenes` variable is set to False in `__main__`. 

### Sample Visualization 
![](https://i.imgur.com/JCRgA0k.jpg)

