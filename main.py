import numpy as np
import tobii_research as tr
import logging

logging.basicConfig(handlers=[logging.FileHandler('output.log', 'w',
                                                  'utf-8')],
                    format='%(name)s - %(levelname)s - %(message)s')
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


from kivy.core.window import Window
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.animation import Animation

from virtual_keyboard import *

import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'texttospeechproject.json'


from os.path import join, dirname
from iconfonts import register


register('default_font', 'fontawesome.ttf',
         join(dirname(__file__), 'fontawesome.fontd'))

from text_to_speech import TextToSpeech


def get_avg_gaze_pos(gaze_data):
    # access gaze data dictionary to get gaze position tuples
    left_gaze_point_xy = gaze_data['left_gaze_point_on_display_area']
    right_gaze_point_xy = gaze_data['right_gaze_point_on_display_area']
    # get 2D gaze positions for left and right eye
    xs = (left_gaze_point_xy[0], right_gaze_point_xy[0])
    ys = (left_gaze_point_xy[1], right_gaze_point_xy[1])

    # if all of the axes have data from at least one eye
    if all([x != -1.0 for x in xs]) and all([y != -1.0 for y in ys]):
        # take x and y averages
        avg_gaze_pos = np.nanmean(xs), np.nanmean(ys)
    else:
        # or if no data, hide points by showing off screen
        avg_gaze_pos = (np.nan, np.nan)
    return avg_gaze_pos


# check if point is inside rectangle
def is_point_inside_rectangle(rect_x0, rect_y0, rect_x1, rect_y1, point_x, point_y):
    if rect_x0 < point_x < rect_x1:
        return rect_y0 < point_y < rect_y1
    return False


# takes x and y coordinates in pixels
def find_letter_based_on_coordinates(letters_coords_list, xy_coor=tuple):
    logging.info("Entered method find_letter_based_on_coordinates")
    logging.info("x coord is: {}".format(xy_coor[0]))
    logging.info("y coord is: {}".format(xy_coor[1]))
    if 0.73 < xy_coor[1] < 0.96:
        logging.info("Point is inside one of the labels")
    # obviously make it to find it based on a map
    for letter_coord in letters_coords_list:
        if is_point_inside_rectangle(letter_coord.x0, letter_coord.y0, letter_coord.x1, letter_coord.y1, xy_coor[0],
                                     xy_coor[1]):
            return letter_coord
    # raise ValueError("Couldn't map a point to a rectangle")


def log_word(array):
    logging.info("Time to collect a word")
    logging.info("Letter array: {}".format(array))
    word = ''
    # check if array is empty maybe
    for letter in array:
        word += letter
    logging.info(f'The word generated is: {word}')
    return word


#  takes coordinates of top left and top right corner
# returns coordinates of the middle of the rectangle
def calculate_middle_of_rectangle(x0, y0, x1, y1):
    rectangle_width = x1 - x0
    rectangle_height = y1 - y0
    x_middle = x0 + rectangle_width / 2
    y_middle = y0 + rectangle_height / 2
    return [x_middle, y_middle]


# to_uppercase <- if it's set to false then change to lowercase
def change_keyboard_layout(to_uppercase, letters_coords_list):
    logging.info("Entered method change_keyboard_layout")
    for letter_coord in letters_coords_list:
        if letter_coord.letter_lowercase != "Lock" and letter_coord.letter_lowercase != "Shift" and letter_coord.letter_lowercase != "ERASE" and letter_coord.letter_lowercase != "TAB" and letter_coord.letter_lowercase != "SPACE" and letter_coord.letter_lowercase != "SUBMIT" and letter_coord.letter_lowercase != "ENTER" and letter_coord.letter_lowercase != "Exit":
            if to_uppercase:
                letter_coord.button_id.text = letter_coord.letter_uppercase
            else:
                letter_coord.button_id.text = letter_coord.letter_lowercase


def is_button_submit_or_prev(button_id, submit_id, previous_text_labels):
    if button_id == submit_id:
        return True
    for i in previous_text_labels:
        if i.button_id == button_id:
            logging.info("Found a prev text label")
            return True
    return False


def is_interval_button(button_id, intervals_list):
    for i in intervals_list:
        if i.button_id == button_id:
            logging.info("Found a button for changing the interval")
            return True
    return False

def get_interval_from_string(letter_string):
    options = {
        "interval_1": 1,
        "interval_2": 2,
        "interval_3": 3,       
        }
    return options[letter_string]

def change_interval_buttons_backgr_color(intervals_list, new_interval_button_id):
    for i in intervals_list:
        if i.button_id == new_interval_button_id:
            i.background_color=(.3, .6, .9, 1)
        else:
            i.background_color=(.3, .6, .7, 1)

import pandas as pd
from scipy.stats import gaussian_kde


def calculate_dot_density(dots_buffer_x, dots_buffer_y):
    names = ["X", "Y"]
    data = tuple(zip(dots_buffer_x, dots_buffer_y))
    df = pd.DataFrame(data, columns=names)
    min_x = df["X"].min()
    max_x = df["X"].max()
    min_y = df["Y"].min()
    max_y = df["Y"].max()
    kernel = gaussian_kde(df.values.T)
    grid_xs, grid_ys = np.mgrid[min_x:max_x:100j, min_y:max_y:100j]
    positions = np.vstack([grid_xs.ravel(), grid_ys.ravel()])
    Z = np.reshape(kernel(positions).T, grid_xs.shape)
    idx = np.unravel_index(np.argmax(Z), Z.shape)
    center = grid_xs[idx], grid_ys[idx]
    return center


class GazeDataInfo():
    def __init__(self, letters_coords_list, gaze_output_frequency, textfield_id, shift_ids_list, lock_id, hidden_label,
                  text_to_speech,
                  my_eyetracker, eye_label, previous_text_labels, submit_button, intervals_list
                  ):
    
        self.list_of_letters = []
        self.previous_button_id = None
        self.old_timestamp = None
        self.dots_buffer_x = []
        self.dots_buffer_y = []
        self.dots_buffer_xy = []
        self.letters_coords_list = letters_coords_list
        self.counter = 0
        self.gaze_output_frequency = gaze_output_frequency
        # starting with uppercase;
        # True for uppercase, false for lowercase
        self.uppercase = False
        self.textfield_id = textfield_id
        self.shift_ids_list = shift_ids_list
        self.shift_on = False
        self.lock_on = False
        self.lock_id = lock_id
        self.dot_counter = 0
        self.hidden_label = hidden_label
        self.text_to_speech = text_to_speech
        self.my_eyetracker = my_eyetracker
        self.eye_label = eye_label
        self.eye_label_initial_color = eye_label.color
        self.previous_text_labels = previous_text_labels
        self.submit_button = submit_button
        self.intervals_list = intervals_list
        self.seconds_to_collect_data = 2

    def subscribe_callback(self, gaze_data):
        time_stamp = gaze_data['device_time_stamp']
        if time_stamp == self.old_timestamp:
            logging.info('no new sample generated')
            return
        else:

            if not gaze_data['left_gaze_point_validity'] and not gaze_data['right_gaze_point_validity']:
                self.eye_label.color = (1, 0, 0, 1)
                return
            else:
                self.eye_label.color = self.eye_label_initial_color

            average_position_ada_coords = get_avg_gaze_pos(gaze_data)
            if np.isnan(average_position_ada_coords[0]) and np.isnan(average_position_ada_coords[1]):
                logging.warning("Dot is not valid, skipping it")
                return

            self.counter += 1
            self.dot_counter += 1

            # mark every 10th dot
            if self.dot_counter > 10:

                letter = find_letter_based_on_coordinates(self.letters_coords_list,
                                                          [average_position_ada_coords[0],
                                                           average_position_ada_coords[1]])

                # revert the previous button color
                if self.previous_button_id is not None and self.previous_button_id != self.lock_id:
                    self.previous_button_id.background_color = (.3, .6, .7, 1)
                    if is_button_submit_or_prev(self.previous_button_id, self.submit_button, self.previous_text_labels):
                        self.previous_button_id.background_color = (.3, .6, .7, 0.5)
                # color the rectangle that represents that letter
                button_id = letter.button_id
                if self.previous_button_id != self.lock_id:
                    button_id.background_color = (1.0, 0.0, 0.0, 1)
                    if is_button_submit_or_prev(button_id, self.submit_button, self.previous_text_labels):

                        button_id.background_color = (1.0, 0.0, 0.0, 0.5)
                self.previous_button_id = button_id
                self.dot_counter = 0

            if self.counter > self.gaze_output_frequency * self.seconds_to_collect_data:

                self.counter = 0
                logging.info("Counter set to: {}".format(self.counter))

                logging.info("Time to find a letter")
                dot_density_xy = calculate_dot_density(self.dots_buffer_x, self.dots_buffer_y)

                letter = find_letter_based_on_coordinates(self.letters_coords_list, dot_density_xy)

                if self.uppercase:
                    letter_string = letter.letter_uppercase
                else:
                    letter_string = letter.letter_lowercase
                logging.info("My letter is: {0}".format(letter_string))
                
                if is_interval_button(button_id, self.intervals_list):
                    new_interval = get_interval_from_string(letter_string)
                    logging.info("Changing the collect interval to {} seconds".format(new_interval))
                    self.seconds_to_collect_data = new_interval
                    change_interval_buttons_backgr_color(self.intervals_list, button_id)

                if letter_string == "Exit":
                    logging.info("Pressed Exit, application will exit")
                    self.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA,
                                                        self.subscribe_callback)
                    logging.info("Unsubscribed from gaze data.")
                    App.get_running_app().stop()
                    Window.close()

                if letter_string.startswith("previous_text"):
                    logging.info("Picked text that is not yet generated. Skipping...")
                    return

                if letter_string == "SUBMIT":
                    logging.info("Found the SUBMIT, now collecting letters to print a word")
                    if not self.list_of_letters:
                        logging.info("No letters in the array, skipping word generation")
                    else:
                        text_to_speak = log_word(self.list_of_letters)
                        self.text_to_speech.text_to_wav(text_to_speak)
                        self.list_of_letters = []
                        self.textfield_id.text = ""

                        size = len(self.previous_text_labels)
                        logging.info("SUBMIT; size = {}".format(size))
                        k = size - 1
                        while k > 0:
                            self.previous_text_labels[k].button_id.text = self.previous_text_labels[
                                k - 1].button_id.text
                            self.previous_text_labels[k].letter_lowercase = self.previous_text_labels[
                                k - 1].letter_lowercase
                            k -= 1
                        self.previous_text_labels[0].button_id.text = text_to_speak
                        self.previous_text_labels[0].letter_lowercase = text_to_speak

                elif letter_string == "Lock":

                    logging.info("Pressed Lock button")

                    if not self.lock_on:
                        logging.info("Pressed Lock button, changing letters to uppercase")
                        self.lock_on = True
                        self.shift_on = True
                        self.lock_id.background_color = (1.0, 0.5, 0.1, 1.0)
                        self.shift_ids_list[0].background_color = (1.0, 0.5, 0.1, 1.0)
                        self.shift_ids_list[1].background_color = (1.0, 0.5, 0.1, 1.0)
                        self.uppercase = True
                        change_keyboard_layout(self.uppercase, self.letters_coords_list)
                    else:
                        logging.info("Pressed Lock button, changing letters to lowercase")
                        self.lock_on = False
                        self.shift_on = True
                        self.lock_id.background_color = (.3, .6, .7, 1)
                        self.shift_ids_list[0].background_color = (.3, .6, .7, 1)
                        self.shift_ids_list[1].background_color = (.3, .6, .7, 1)
                        self.uppercase = False
                        change_keyboard_layout(self.uppercase, self.letters_coords_list)

                elif letter_string == "Shift":
                    logging.info("Pressed Shift button")
                    if self.shift_on == False:
                        self.shif_on = True
                        logging.info("Checking the value of self.shift_on={}".format(self.shift_on))
                        self.uppercase = True
                        self.shift_ids_list[0].background_color = (1.0, 0.5, 0.1, 1.0)
                        self.shift_ids_list[1].background_color = (1.0, 0.5, 0.1, 1.0)
                        change_keyboard_layout(self.uppercase, self.letters_coords_list)
                    else:
                        self.shif_on = False
                        self.uppercase = False
                        self.shift_ids_list[0].background_color = (.3, .6, .7, 1)
                        self.shift_ids_list[1].background_color = (.3, .6, .7, 1)
                        change_keyboard_layout(self.uppercase, self.letters_coords_list)

                elif letter_string == "ERASE":
                    logging.info("List of letters currently wrote: {}".format(self.list_of_letters))
                    if self.list_of_letters:
                        logging.info("Erasing the previous letter")
                        self.list_of_letters.pop()
                        text_to_show = log_word(self.list_of_letters)
                        # PLUS update text field with this change
                        self.textfield_id.text = text_to_show
                    else:
                        logging.info("There were no letters to erase")

                else:

                    if letter_string == "ENTER":
                        letter_string = "\n"
                    elif letter_string == "SPACE":
                        letter_string = " "
                    elif letter_string == "TAB":
                        letter_string = "\t"

                    logging.info("Appending the letter to a list")
                    self.list_of_letters.append(letter_string)
                    text_to_show = log_word(self.list_of_letters)
                    # PLUS update text field with this change
                    self.textfield_id.text = text_to_show
                    self.hidden_label.text = letter_string
                    logging.info("Time to animate the label")

                    initial_pos_x = self.hidden_label.pos_hint['x']
                    initial_pos_y = self.hidden_label.pos_hint['y']
                    animation = Animation(pos_hint={'x': initial_pos_x, 'y': initial_pos_y}, t='in_circ', d=0.3,
                                          opacity=1)
                    animation += Animation(pos_hint={'x': initial_pos_x, 'y': initial_pos_y}, t='out_sine', d=0.3,
                                           opacity=0)
                    logging.info("Starting animation")
                    animation.start(self.hidden_label)
                    logging.info("Animation done")

                # 5. empty the buffer
                self.dots_buffer_x = []
                self.dots_buffer_y = []
                # self.dots_buffer_xy = []
            else:
                # add a new dot to a buffer
                logging.info("Adding new dot to buffer")
                self.dots_buffer_x.append(average_position_ada_coords[0])
                self.dots_buffer_y.append(average_position_ada_coords[1])
                # self.dots_buffer_xy.append([average_position_ada_coords[0], average_position_ada_coords[1]])

        def add_latest_text_to_label(self, text):
            size = self.previous_text_labels.size
            i = 0
            while i < size:
                self.previous_text_labels[i + 1].text = self.previous_text_labels[i].text
            self.previous_text_labels[0].text = text


class EyetrackerInfo:
    def __init__(self):
        self.my_eyetracker = self.get_first_eyetracker()

    # get the first eyetracker
    def get_first_eyetracker(self):
        found_eyetrackers = tr.find_all_eyetrackers()
        eyetrackers_count = len(found_eyetrackers)
        if eyetrackers_count == 0:
            logging.error("Eyetracker not found!")
            raise ValueError("Eyetracker not found")
        self.my_eyetracker = found_eyetrackers[0]
        assert isinstance(self.my_eyetracker, object)
        self.print_eyetracker_info()
        self.check_eyetracker_capabilities()
        self.get_gaze_output_frequency()
        self.set_gaze_output_frequency_to_minimum()
        return self.my_eyetracker

    def print_eyetracker_info(self):
        logging.info("Address: " + self.my_eyetracker.address)
        logging.info("Model: " + self.my_eyetracker.model)
        logging.info("Name (It's OK if this is empty): " + self.my_eyetracker.device_name)
        logging.info("Serial number: " + self.my_eyetracker.serial_number)

    def check_eyetracker_capabilities(self):
        if tr.CAPABILITY_CAN_SET_DISPLAY_AREA in self.my_eyetracker.device_capabilities:
            logging.info("The display area can be set on the eye tracker.")
        else:
            logging.info("The display area can not be set on the eye tracker.")

        if tr.CAPABILITY_HAS_EXTERNAL_SIGNAL in self.my_eyetracker.device_capabilities:
            logging.info("The eye tracker can deliver an external signal stream.")
        else:
            logging.info("The eye tracker can not deliver an external signal stream.")

        if tr.CAPABILITY_HAS_EYE_IMAGES in self.my_eyetracker.device_capabilities:
            logging.info("The eye tracker can deliver an eye image stream.")
        else:
            logging.info("The eye tracker can not deliver an eye image stream.")

        if tr.CAPABILITY_HAS_GAZE_DATA in self.my_eyetracker.device_capabilities:
            logging.info("The eye tracker can deliver a gaze data stream.")
        else:
            logging.info("The eye tracker can not deliver a gaze data stream.")

        if tr.CAPABILITY_HAS_HMD_GAZE_DATA in self.my_eyetracker.device_capabilities:
            logging.info("The eye tracker can deliver a HMD gaze data stream.")
        else:
            logging.info("The eye tracker can not deliver a HMD gaze data stream.")

        if tr.CAPABILITY_CAN_DO_SCREEN_BASED_CALIBRATION in self.my_eyetracker.device_capabilities:
            logging.info("The eye tracker can do a screen based calibration.")
        else:
            logging.info("The eye tracker can not do a screen based calibration.")

        if tr.CAPABILITY_CAN_DO_MONOCULAR_CALIBRATION in self.my_eyetracker.device_capabilities:
            logging.info("The eye tracker can do a monocular calibration.")
        else:
            logging.info("The eye tracker can not do a monocular calibration.")

        if tr.CAPABILITY_CAN_DO_HMD_BASED_CALIBRATION in self.my_eyetracker.device_capabilities:
            logging.info("The eye tracker can do a HMD screen based calibration.")
        else:
            logging.info("The eye tracker can not do a HMD screen based calibration.")

        if tr.CAPABILITY_HAS_HMD_LENS_CONFIG in self.my_eyetracker.device_capabilities:
            logging.info("The eye tracker can get/set the HMD lens configuration.")
        else:
            logging.info("The eye tracker can not get/set the HMD lens configuration.")

    def get_gaze_output_frequency(self):
        gaze_output_frequency = self.my_eyetracker.get_gaze_output_frequency()
        logging.info("The eye tracker's gaze output frequency is {0} Hz.".format(gaze_output_frequency))
        return gaze_output_frequency

    def set_gaze_output_frequency_to_minimum(self):
        current_gaze_output_frequency = self.my_eyetracker.get_gaze_output_frequency()
        for gaze_output_frequency in self.my_eyetracker.get_all_gaze_output_frequencies():
            if gaze_output_frequency < current_gaze_output_frequency:
                current_gaze_output_frequency = gaze_output_frequency
        self.my_eyetracker.set_gaze_output_frequency(current_gaze_output_frequency)
        logging.info("Gaze output frequency set to {0} Hz.".format(current_gaze_output_frequency))


class MyApp(App):
    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        virtualKeyboard = VirtualKeyboard()
        self.letters_coords_list = virtualKeyboard.letters_coords_list
        self.textfield = virtualKeyboard.textinput
        self.shift_ids_list = virtualKeyboard.shift_ids_list
        self.lock_id = virtualKeyboard.lock_id
        self.hidden_label = virtualKeyboard.hidden_label
        self.eye_label = virtualKeyboard.eye_label
        self.previous_text_labels = virtualKeyboard.previous_text_labels
        self.intervals_list = virtualKeyboard.intervals_list
        self.submit_button = virtualKeyboard.submit_button
        return virtualKeyboard

    def on_start(self, **kwargs):
        self.gaze_data_info = GazeDataInfo(self.letters_coords_list, self.gaze_output_frequency, self.textfield,
                                           self.shift_ids_list, self.lock_id, self.hidden_label, self.text_to_speech,
                                           self.eyetracker_info.my_eyetracker, self.eye_label,
                                           self.previous_text_labels, self.submit_button, self.intervals_list
                                           )

        # subscribe
        logging.info("Subscribing to gaze data for eye tracker with serial number {0}.".format(
            self.eyetracker_info.my_eyetracker.serial_number))
        self.eyetracker_info.my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self.gaze_data_info.subscribe_callback,
                                                        as_dictionary=True)

    def on_request_close(self, *args):
        self.textpopup(title='Излаз', text='Да ли сте сигурни?')
        return True

    def textpopup(self, title='', text=''):
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=text))
        mybutton = Button(text='Да', size_hint=(1, 0.25))
        box.add_widget(mybutton)
        popup = Popup(title=title, content=box, size_hint=(None, None), size=(600, 300))
        mybutton.bind(on_release=self.on_release)
        popup.open()

    def on_release(self, event):
        self.stop
        Window.close()

    def set_eyetracker_nfo(self, eyetracker_info):
        self.eyetracker_info = eyetracker_info
        self.gaze_output_frequency = eyetracker_info.get_gaze_output_frequency()

    def set_text_to_speech(self, text_to_speech):
        self.text_to_speech = text_to_speech




class MainClass:
    def __init__(self):
        self.my_main()

    def my_main(self):
        Window.clearcolor = (0, 0, 0, 1)
        eyetracker_info = None
        my_app = None
        try:
            # initialize eyetracker
            eyetracker_info = EyetrackerInfo()
            text_to_speech = TextToSpeech()

            my_app = MyApp()
            my_app.set_eyetracker_nfo(eyetracker_info)
            my_app.set_text_to_speech(text_to_speech)

            logging.info("Starting the application")
            my_app.run()
        except ValueError as err:
            logging.error(err)
        except TypeError as err:
            logging.error(err)
        finally:
            # unsubscribe
            if eyetracker_info is not None:
                if my_app is not None:
                    if my_app.gaze_data_info is not None:
                        eyetracker_info.my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA,
                                                                       my_app.gaze_data_info.subscribe_callback)
                        logging.info("Unsubscribed from gaze data.")
            logging.info("Program execution complete")

if __name__ == "__main__":
    main_class = MainClass()