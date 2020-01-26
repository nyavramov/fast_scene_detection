import cv2
import matplotlib.pyplot as plt


class Video:
    """Class that handles storing and visualizing scenes of a particular video"""
    def __init__(self, scenes):
        """
        :param scenes: A list of sorted Scene object
        """
        self.scenes = scenes
        self.sorted_scenes = None

    def get_scenes(self, n=40):
        """Extracts the top n scenes from a video, ranked by the largest changes in consecutive perceptual hashes

        :param n: an integer to determine the number of scenes to extract from a video
        :return None:
        """
        # Sort the scenes list according to each scene's hash change, from largest to smallest
        self.sorted_scenes = sorted(self.scenes, key=lambda scene_key: scene_key.hash_delta, reverse=True)

        # Truncate the list to preserve only the largest hash change
        self.sorted_scenes = self.sorted_scenes[:n]

        # Resort the scenes according to the time they occurred
        self.sorted_scenes = sorted(self.sorted_scenes, key=lambda scene_key: scene_key.frame_number)

        print(f"These are the top {n} scene timestamps:")
        for scene in self.sorted_scenes:
            print(f"- {scene.time_stamp}")

    def visualize_scenes(self):
        """Once we've found top N scene changes, use this function to visualize each scene according to time stamp"""
        '''
        Suppose we want to have twice as many columns as there are rows in visualization
            number_of_scenes = number_of_rows * number_of_columns
            number_of_columns = 2 * number_of_rows
            --> number_of_scenes = number_of_rows * (2 * number_of_rows)
            --> number_of_columns = 2 * (sqrt(number_of_scenes / 2))
        '''
        number_of_scenes = len(self.sorted_scenes)
        number_of_columns = int(2 * ((number_of_scenes / 2) ** 0.5))
        number_of_rows = int((number_of_scenes / 2) ** 0.5)

        just_incremented_rows = False

        # Enable interactivity mode to allow us to continuously display plots
        plt.ion()

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

        fig = plt.figure()
        fig.canvas.manager.full_screen_toggle()

        # Display each scene as a subplot in matplotlib
        for counter, scene in enumerate(self.sorted_scenes):

            y = fig.add_subplot(number_of_rows, number_of_columns, counter + 1)

            plt.subplots_adjust(left=0, bottom=0, right=1.0, top=0.99, wspace=0.0, hspace=0.07)
            y.imshow(cv2.cvtColor(scene.frame, cv2.COLOR_BGR2RGB))

            # If want to continuously display plots for multiple videos in directory, we need to insert this pause
            # https://stackoverflow.com/questions/11874767/how-do-i-plot-in-real-time-in-a-while-loop-using-matplotlib
            plt.pause(.0000001)

            # Label each scene with its corresponding time
            plt.title(scene.time_stamp)

            y.axes.get_xaxis().set_visible(False)
            y.axes.get_yaxis().set_visible(False)

        plt.show()
