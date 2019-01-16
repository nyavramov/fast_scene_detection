from PIL import Image 
from tqdm import tqdm 

import imagehash
import cv2
import sys
import os
import glob
import time
import matplotlib.pyplot as plt

HASH_SIZE = 128 
STEPSIZE_CONSTANT = 0.00429584
SCENE_LIMIT = 80

# Once we've found the top N scene changes, use this function to visualize each
# scene according to its time stamp
def visualize_scene_changes(frame_number_time_list, pathOfSourceVideo):
    
    cap = cv2.VideoCapture(pathOfSourceVideo)
    fig = plt.figure()

    number_of_scenes = len(frame_number_time_list)

    '''
    We need to determine the correct number of rows & columns for our visualization
    Suppose that number_of_columns * number_of_rows = number_of_scenes
    Also, suppose we want to have twice as many columns as there are rows
    
    Therefore:
        
        number_of_scenes = number_of_rows * number_of_columns
        number_of_columns = 2 * number_of_rows
        --> number_of_scenes = number_of_rows * (2 * number_of_rows)
        --> number_of_scenes = 2 * number_of_rows ^ 2
        --> number_of_scenes / 2 = number_of_rows ^ 2
        --> number_of_rows = sqrt(number_of_scenes / 2)
        --> number_of_columns = 2 * (sqrt(number_of_scenes / 2))

    '''
    number_of_columns = int(2 * ((number_of_scenes / 2) ** 0.5))
    number_of_rows    = int((number_of_scenes / 2) ** 0.5)
    
    just_incremented_rows = False

    # Since we're calling int() on column/row values, number_of_columns * number_of_rows may be < number_of_scenes
    # This happens since int() may round a decimal down
    # Increment either row or column number until their product is > number_of_scenes
    while number_of_columns * number_of_rows < number_of_scenes:
        if not just_incremented_rows:
            number_of_rows += 1
            just_incremented_rows = True
        else:
            number_of_columns += 1
            just_incremented_rows = False
    
    # Display each scene as a subplot in matplotlib
    for counter, scene in enumerate(frame_number_time_list[0:number_of_scenes]):

        y = fig.add_subplot(number_of_rows, number_of_columns, counter + 1)
        plt.subplots_adjust(left=0,bottom=0,right=1.0,top=0.99,wspace=0.0,hspace=0.07)

        try:
            # Tell OpenCV to start reading from the scene's frame number
            cap.set(cv2.CAP_PROP_POS_FRAMES, scene[0])
            ret, frame = cap.read()
        except Exception as e:
            print(e)
            continue

        y.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # If want to continuously display plots for multiple videos in directory, we need to insert this pause
        # https://stackoverflow.com/questions/11874767/how-do-i-plot-in-real-time-in-a-while-loop-using-matplotlib
        plt.pause(.0000001)

        # Label each scene with its corresponding time 
        plt.title(scene[1])

        y.axes.get_xaxis().set_visible(False)
        y.axes.get_yaxis().set_visible(False)

    plt.show()

# We'll use this if the user provides a directory to allow us to extract all the videos in that directory
def createVideoList(directory):
    videosList = []
    extensions = ["*.mp4", "*.wmv","*.avi", "*.mpeg", "*.mkv"]
    fileTypes  = [os.path.join(directory, fileType) for fileType in extensions]
    
    for fileType in fileTypes:
        aVideo = glob.glob(fileType)
        if (len(aVideo) > 0):
            videosList.extend(aVideo) 

    return (videosList)    

def iterate_through_video_frames(pathOfSourceVideo, visualize_scenes = False):

    current_frame_number = 0
    cap                  = cv2.VideoCapture(pathOfSourceVideo)
    frames_per_second    = cap.get(cv2.CAP_PROP_FPS)
    number_of_frames     = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    progress_bar         = tqdm(total = number_of_frames)

    previous_frame_hash, current_frame_hash = None, None
    
    frame_number_time_list            = []
    hash_difference_frame_number_list = []
    
    # The stepsize defines how many frames we skip when we compare hashes to see if the scene has changed
    # We define a stepsize constant so we can adapt the stepsize based on the length of the video we're breaking 
    # into scenes
    stepsize = int(number_of_frames * STEPSIZE_CONSTANT)
    
    if stepsize < 1:
        stepsize = 1
    
    # Iterate through all the video frames while the capture is open
    while cap.isOpened():
        current_frame_number += 1
        progress_bar.update(1)

        # Allows us to skip some number of frames defined by stepsize
        # Note: Since setting CAP_PROP_POS_FRAMES is slow, we'll need a sufficiently step size for us to 
        # take advantage of the speed boost that it offers in terms of skipping frames
        if current_frame_number % stepsize != 0:
            continue

        # Tell OpenCV to start reading the video from the current frame number
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_number)
        ret, frame = cap.read()

        if not ret:
            cap.release()
            break

        frame = Image.fromarray(frame)
        
        # Handle special case where we're just reading the first frame, and there's nothing else to compare it to
        if previous_frame_hash is None:
            previous_frame_hash = imagehash.phash(frame, hash_size = HASH_SIZE)
        else:
            # Calculate the current frame's hash and calculate the Hamming distance in percent form so we can compare it to previous frame later
            current_frame_hash = imagehash.phash(frame, hash_size = HASH_SIZE)
            hash_difference = previous_frame_hash - current_frame_hash
            previous_frame_hash = current_frame_hash
            hash_difference_frame_number_list.append((hash_difference, current_frame_number))

    # Since we have a list of lists, sort list by 0th index of each element, and truncate list to first N elements defined by SCENE_LIMIT constant
    # Doing this so we can keep track of N=40 biggest changes in hamming distance and use those as scene change indicators
    hash_difference_frame_number_list.sort(key = lambda x: x[0])
    hash_difference_frame_number_list = hash_difference_frame_number_list[:SCENE_LIMIT]
    hash_difference_frame_number_list.sort(key = lambda x: x[1]) # Return list to original order to keep it temporally coherent
    
    for element in hash_difference_frame_number_list:
        current_time = int(element[1] / frames_per_second)
        current_time = time.strftime('%H:%M:%S', time.gmtime(current_time))
        frame_number_time_list.append((element[1], current_time))
    
    hash_difference_frame_number_list.sort(key = lambda x: x[0])
    
    for frame_number, time_stamp in frame_number_time_list:
        print(frame_number, time_stamp)

    # Check if the user has requested a visualization of each scene using matplotlib
    if visualize_scenes:
        visualize_scene_changes(frame_number_time_list, pathOfSourceVideo)

    # In case we want to call this function for required timestamps from another python file
    return frame_number_time_list
        
if __name__ == '__main__':
    # Enable interactivity mode to allow us to continuously display plots
    plt.ion()

    if os.path.isfile(sys.argv[1]):
        iterate_through_video_frames(sys.argv[1], True)
    elif os.path.isdir(sys.argv[1]):
        videos = createVideoList(sys.argv[1])
        [iterate_through_video_frames(video, True) for video in videos]
    else:
        print("Not a file or directory! Please provide a valid file path or directory path.")

    input("Press ENTER to exit.")