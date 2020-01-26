import _pickle as pickle
import os
from pathlib import Path


class VideoLibrary:
    """Class that handles storing previously segmented scenes for later use"""
    def __init__(self, video_list):
        """
        :param video_list: a list of Video Objects
        """
        self.video_list = video_list

    def append(self, video):
        """Appends a video to the library"""
        self.video_list.append(video)

    def save(self, save_directory, file_name="video_collection"):
        """Saves the VideoLibrary object

        :param save_directory: a string representing a destination path to save to
        :param file_name: a string representing the name of the saved file
        :return None:
        """
        Path(save_directory).mkdir(parents=True, exist_ok=True)

        with open(os.path.join(save_directory, file_name), "wb") as fp:
            pickle.dump(self.video_list, fp)

    def open(self, library_path):
        """Loads a video list from a source path

        :param library_path: a string representing a path containing a video library pickle object"""
        with open(library_path, "rb") as fp:
            self.video_list = pickle.load(fp)
