import cv2
import imagehash
from PIL import Image
from tqdm import tqdm

from .scene import Scene
from .video import Video
from .video_file_handler import VideoFileHandler


class SceneExtractor:
    """Class for handling videos and segmenting them into scenes"""
    def __init__(self, video_source, step_size_constant=0.00429584, video_library=None):
        self.hash_size = 128
        self.step_size_constant = step_size_constant
        self.video_library = video_library

        self.file_handler = VideoFileHandler(video_source)

    @staticmethod
    def get_video_details(video_capture):
        """Extracts the frames per second and number of frames in an given video input

        :param video_capture: a cv2 video capture object
        :return frames_per_second: a float value storing the video frames per second
        :return number_of_frames: an integer storing the number of frames in an input video
        """
        frames_per_second = video_capture.get(cv2.CAP_PROP_FPS)
        number_of_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

        return frames_per_second, number_of_frames

    def process_scenes(self):
        """Iterates through a list of video paths and performs processing on each video"""
        for video_path in self.file_handler.video_paths_list:
            segmented_video = self.segment_video(video_path)

            if self.video_library is not None:
                self.video_library.append(segmented_video)

    def process_frames(self, video_capture, number_of_frames, frames_per_second, step_size):
        """Iterates through a stream of video frames and extracts hashes to determine video scenes

        :param video_capture: a cv2 video capture object
        :param number_of_frames: an integer storing the number of frames in an input video
        :param frames_per_second: a float value storing the video frames per second
        :param step_size: an integer that determines rate at which to skip frames. i.e. if step_size = 3, the 1st frame
                          is read, 3 frames are skipped, the 4th frame is read, 3 are skipped, the 7th read and so on
        :return scenes_list: a list of Scene objects
        """
        previous_frame_hash, current_frame_hash, hash_delta, current_frame_number = None, None, None, 0
        scenes_list = []

        # Iterate through all the video frames while the capture is open
        progress_bar = tqdm(total=number_of_frames)
        while video_capture.isOpened():
            current_frame_number += 1
            progress_bar.update(1)

            # Allows us to skip some number of frames defined by stepsize
            # Note: Since setting CAP_PROP_POS_FRAMES is slow, we'll need a sufficiently large step size for us to
            # take advantage of the speed boost that it offers in terms of skipping frames
            if current_frame_number % step_size != 0:
                continue

            # Tell OpenCV to start reading the video from the current frame number
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, current_frame_number)
            ret, frame = video_capture.read()

            if not ret:
                video_capture.release()
                break

            frame = Image.fromarray(frame)
            previous_frame_hash, hash_delta = self.calculate_frame_hashes(frame, previous_frame_hash, hash_delta)

            if hash_delta is not None:
                scenes_list.append(Scene(frame, hash_delta, current_frame_number, frames_per_second))

        return scenes_list

    def calculate_frame_hashes(self, frame, previous_frame_hash, hash_delta):
        """Uses the imagehash library to calculate the perceptual hash differences between frames

        :param frame: a pillow image object
        :param previous_frame_hash: the perceptual hash of the previously read frame
        :param hash_delta: the change in the perceptual hash, i.e. the Hamming distance
        :return previous_frame_hash: the perceptual hash of the previously read frame
        :return hash_delta: the change in the perceptual hash, i.e. the Hamming distance
        """
        # Handle special case where we're just reading the first frame, and there's nothing else to compare it to
        if previous_frame_hash is None:
            previous_frame_hash = imagehash.phash(frame, hash_size=self.hash_size)
        else:
            # Calculate the current frame's hash and calculate the Hamming distance so we can
            # compare it to previous frame
            current_frame_hash = imagehash.phash(frame, hash_size=self.hash_size)
            hash_delta = previous_frame_hash - current_frame_hash
            previous_frame_hash = current_frame_hash

        return previous_frame_hash, hash_delta

    def segment_video(self, video_path):
        """Reads and segments a given video into scenes

        :param video_path: a string representing a path to a video
        :return video: a Video object containing scenes
        """
        # Create a video capture and get the video details
        video_capture = cv2.VideoCapture(video_path)
        frames_per_second, number_of_frames = self.get_video_details(video_capture)

        # The stepsize defines how many frames we skip when we compare hashes to see if the scene has changed
        # We define a stepsize constant so we can adapt the stepsize based on the length of the video we're breaking
        # into scenes
        step_size = int(number_of_frames * self.step_size_constant)
        if step_size < 1:
            step_size = 1

        # Get the scenes and create the video object from them
        scenes_list = self.process_frames(video_capture, number_of_frames, frames_per_second, step_size)
        video = Video(scenes_list)

        return video
