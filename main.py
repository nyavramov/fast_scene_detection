import argparse

from fast_segmentation.scene_extractor import SceneExtractor
from fast_segmentation.video_library import VideoLibrary


def arg_parser():
    """Parses user's command line input"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_path', action='store', help='A video source file or directory containing videos',
                        dest='source_path')
    parser.add_argument('--save_path', action='store', help='A path to which you would like to save the segmented '
                                                            'videos', dest='save_path')
    parser.add_argument('--library_path', action='store', help='A path to a pickled video video library object',
                        dest='library_path')
    parser.add_argument('--visualize_scenes', action='store_true', help='Whether to visualize scenes or not',
                        dest='visualize_scenes')
    cmdline_args = parser.parse_args()

    return cmdline_args


def main():
    # Parse user command line arguments and initialize the video library object
    cmdline_args = arg_parser()
    video_library = VideoLibrary(video_list=[])

    # Check if we're going to open previously extracted scenes or if we'll need to extract them
    if cmdline_args.library_path:
        print(f"Opening a video library from path: {cmdline_args.library_path}")
        video_library.open(library_path=cmdline_args.library_path)
    elif cmdline_args.source_path:
        print(f"Extracting scenes from path: {cmdline_args.source_path}")
        extractor = SceneExtractor(video_source=cmdline_args.source_path, number_scenes=40, step_size_constant=0.008,
                                   video_library=video_library)
        extractor.process_scenes()

    # Print the scene timestamp and, optionally, visualize the scenes
    for segmented_video in video_library.video_list:
        segmented_video.get_scenes(n=40)

        if cmdline_args.visualize_scenes:
            segmented_video.visualize_scenes()

    # If user has specified path, save the video
    if cmdline_args.save_path:
        print(f"Saving segmented videos to library at: {cmdline_args.save_path}")
        video_library.save(save_directory=cmdline_args.save_path)

    # Ask for user input so the visualization doesn't close immediately
    input("Press ENTER to exit.")


if __name__ == '__main__':
    main()
