from datetime import timedelta

import numpy as np


class Scene:
    """Class intended to store scene attributes for later processing"""
    def __init__(self, frame, hash_delta, frame_number, frames_per_second):
        self.frame = np.array(frame)
        self.hash_delta = hash_delta
        self.frame_number = frame_number
        self.time_stamp = timedelta(seconds=frame_number / frames_per_second)
