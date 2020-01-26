class InvalidPathException(Exception):
    def __init__(self):
        Exception.__init__(self, "The path you've provided must be a supported video file path or a directory "
                                 "containing supported video files")
