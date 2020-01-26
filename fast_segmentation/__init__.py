import glob
import os

from .exceptions import InvalidPathException


class VideoFileHandler:
    """Class for parsing and handling video input sources"""
    def __init__(self, video_source):
        self.video_source = video_source

        # Define valid file extensions and initialize paths list store
        self.valid_file_extensions = [".mp4", ".wmv", ".avi", ".mpeg", ".mkv"]
        self.video_paths_list = []

        self.parse_video_source()

    def parse_video_source(self):
        """Creates a list of videos from a video or directory path"""
        # If the video source given is a directory, get all the files in that directory and extract valid video paths
        if os.path.isdir(self.video_source):
            # Compose a list of paths for use in the glob module
            glob_paths = [os.path.join(self.video_source, f"*{extension}") for extension in self.valid_file_extensions]

            # Gather the video file paths
            for glob_path in glob_paths:
                full_video_path = glob.glob(glob_path)
                # Ensure added globs are non-empty
                if len(full_video_path) > 0:
                    self.video_paths_list.extend(full_video_path)

            if len(self.video_paths_list) == 0:
                raise InvalidPathException
        # If the given path is a file and ends with a valid extension
        elif os.path.isfile(self.video_source) and self.video_source.endswith(tuple(self.valid_file_extensions)):
            self.video_paths_list.append(self.video_source)
        else:
            raise InvalidPathException
