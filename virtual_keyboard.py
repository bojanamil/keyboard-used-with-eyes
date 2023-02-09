from kivy.uix.textinput import TextInput


from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from special_widgets import RoundedButton
from special_widgets import SpecialLabel
from special_widgets import ButtonWithBorder

from iconfonts import icon


# matrix of letters layout
# Reversed because of Kivy coordinates
letters_layout_lowercase = [
    ["Shift", "<", "џ", "ц", "в", "б", "SPACE", "SPACE", "SPACE", "н", "м", ",", ".", "-", "Shift"],
    ["Lock", "Lock", "а", "с", "д", "ф", "г", "х", "ј", "к", "л", "ч", "ћ", "ENTER", "ENTER"],
    ["TAB", "TAB", "љ", "њ", "е", "р", "т", "з", "у", "и", "о", "п", "ш", "ђ", "ж"],
    ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "'", "+", "ERASE", "ERASE"]
]

letters_layout_uppercase = [
    ["Shift", "<", "Џ", "Ц", "В", "Б", "SPACE", "SPACE", "SPACE", "Н", "М", ",", ".", "-", "Shift1"],
    ["Lock", "Lock", "А", "С", "Д", "Ф", "Г", "Х", "Ј", "К", "Л", "Ч", "Ћ", "ENTER", "ENTER"],
    ["TAB", "TAB", "Љ", "Њ", "Е", "Р", "Т", "З", "У", "И", "О", "П", "Ш", "Ђ", "Ж"],
    ["~", "!", "\"", "#", "$", "%", "&", "/", "(", ")", "=", "?", "*", "ERASE", "ERASE"]
]


class LetterCoords:
    def __init__(self, button_id, x0, y0, width, height, letter_uppercase, letter_lowercase):
        self.button_id = button_id
        self.x0 = x0
        self.y0 = y0
        self.x1 = x0 + width
        self.y1 = y0 + height
        self.letter_uppercase = letter_uppercase
        self.letter_lowercase = letter_lowercase
        print("------------------------------")
        print("Printing letter coords data:")
        print("------------------------------")
        print("x0 : {}".format(self.x0))
        print("y0 : {}".format(self.y0))
        print("x1 : {}".format(self.x1))
        print("y1 : {}".format(self.y1))
        print("letter uppercase : {}".format(self.letter_uppercase))
        print("letter lowercase : {}".format(self.letter_lowercase))

class VirtualKeyboard(FloatLayout):
    def __init__(self, **kwargs):
        super(VirtualKeyboard, self).__init__(**kwargs)

        num_of_rows = 4
        num_of_cols = 15

        size_hint_x = 1 / (num_of_cols + 1)
        margin = size_hint_x / 2
        # I want it to take half a screen
        size_hint_y = 1 / (2 * num_of_rows)

        self.letters_coords_list = []
        self.shift_ids_list = []
        self.lock_id = None
        self.intervals_list = []
    
        row_counter = 0
        column_counter = 0

        i = margin
        j = 0.3
        while row_counter < num_of_rows:
            while column_counter < num_of_cols:
                x_coord = i
                y_coord = 1 - (j + size_hint_y)
                print("letters_layout_uppercase[{}][{}]".format(row_counter, column_counter))
                letter_lowercase = letters_layout_lowercase[row_counter][column_counter]
                letter_uppercase = letters_layout_uppercase[row_counter][column_counter]
                if letter_lowercase != "NONE":
                    size_x = size_hint_x
                    if letter_lowercase == "TAB" or letter_lowercase == "Lock" or letter_lowercase == "ERASE" or letter_lowercase == "ENTER":
                        size_x = size_hint_x * 2
                        column_counter += 1
                    elif letter_lowercase == "SPACE":
                        size_x = size_hint_x * 3
                        column_counter += 2
                    btn = ButtonWithBorder(text=letter_lowercase,
                                           background_color=(.3, .6, .7, 1),
                                           # background_normal='',
                                           size_hint=(size_x, size_hint_y),
                                           pos_hint={'x': i, 'y': j},
                                           font_size=24
                                           )
                    self.add_widget(btn)
                    if letter_lowercase == "Shift":
                        self.shift_ids_list.append(btn)
                    if letter_lowercase == "Lock":
                        self.lock_id = btn
                    letter_coords = LetterCoords(btn, x_coord, y_coord, size_hint_x, size_hint_y, letter_uppercase,
                                                 letter_lowercase)
                    self.letters_coords_list.append(letter_coords)
                    if letter_lowercase == "TAB" or letter_lowercase == "Lock" or letter_lowercase == "ERASE" or letter_lowercase == "ENTER":
                        i += size_hint_x
                    elif letter_lowercase == "SPACE":
                        i += size_hint_x * 2
                i += size_hint_x
                column_counter += 1
            j += size_hint_y
            i = margin
            column_counter = 0
            row_counter += 1

        submit_x = (4 - 5 * size_hint_x) / 6 + size_hint_x * 0.5
        submit_x_size = size_hint_x * 2
        submit_y_size = 0.2
        submit_y = (0.3 - submit_y_size) / 2

        self.submit_button = RoundedButton(text="%s" % (icon('fa-play', 64)), markup=True,
                                           size_hint=(submit_x_size, submit_y_size),
                                           pos_hint={'x': submit_x, 'y': submit_y},
                                           )
        self.add_widget(self.submit_button)

        submit_coords = LetterCoords(self.submit_button, submit_x, 1 - (submit_y + submit_y_size), submit_x_size,
                                     submit_y_size, "SUBMIT", "SUBMIT")
        self.letters_coords_list.append(submit_coords)

        text_size_x = 1 / 3 - size_hint_x
        # text_x = 1 / 6
        text_x = (2 - 7 * size_hint_x) / 6 + size_hint_x * 1.5
        self.textinput = TextInput(text="",
                                   font_size = 24,
                                   size_hint=(text_size_x, submit_y_size),
                                   pos_hint={'x': text_x, 'y': submit_y},
                                   readonly=True,
                                   background_color=(230/255, 230/255, 230/255, 1)
                                   )
        self.add_widget(self.textinput)

        self.hidden_label = Label(text='Б',
                                  size_hint=(size_hint_x * 2, size_hint_y * 2),
                                  pos_hint={'x': 0.5 - size_hint_x,
                                            'y': 0.5 - size_hint_y},
                                   opacity=0,
                                  font_size=self.width,
                                  color=(1, 1, 0, 1)
                                  )
        self.add_widget(self.hidden_label)

        self.add_icons_to_buttons()
        self.add_header()
        self.add_previous_text_labels(size_hint_x, margin, submit_y, submit_y_size)
        self.add_pick_intervals(margin)

    def add_icons_to_buttons(self):
        for letter in self.letters_coords_list:
            if letter.letter_lowercase == 'Shift':
                letter.button_id.text = "%s" % (icon('fa-arrow-up', 36))
                letter.button_id.markup = True
            if letter.letter_lowercase == 'ERASE':
                letter.button_id.text = "%s" % (icon('fa-backspace', 36))
                letter.button_id.markup = True
            if letter.letter_lowercase == 'Lock':
                letter.button_id.text = "%s" % (icon('fa-arrow-alt-circle-up', 36))
                letter.button_id.markup = True
            if letter.letter_lowercase == 'TAB':
                letter.button_id.text = "%s" % (icon('fa-long-arrow-alt-right', 36))
                letter.button_id.markup = True
            if letter.letter_lowercase == 'SPACE':
                letter.button_id.text = ""
            if letter.letter_lowercase == 'ENTER':
                letter.button_id.text = "%s" % (icon('fa-chevron-down', 36))
                letter.button_id.markup = True

    def add_header(self):
        empty_label = Label(
            size_hint=(.8, 1 / 6), pos_hint={'y': 8 / 9, 'x': 0})
        self.eye_label = Label(text="%s " % (icon('fa-eye', 36)),
                               color=(204 / 255, 204 / 255, 179 / 255, 1),
                               size_hint=(.05, 1 / 12), pos_hint={'y': 8 / 9, 'x': 0.8}, markup=True)

        wifi_label = Label(text="%s" % (icon('fa-wifi', 36)),
                           color=(204 / 255, 204 / 255, 179 / 255, 1),
                           size_hint=(.05, 1 / 12), pos_hint={'y': 8 / 9, 'x': 0.85}, markup=True)
        exit_button = Button(text="%s" % (icon('fa-door-open', 36)),
                             background_normal='',
                             background_color=(0, 0, 0, 1),
                             color=(204 / 255, 204 / 255, 179 / 255, 1),
                             size_hint=(.05, 1 / 12), pos_hint={'y': 8 / 9, 'x': 0.9}, markup=True)
        exit_button_coords = LetterCoords(exit_button, 0.9, 1 - (8 / 9 + 1 / 12), 0.05, 1 / 12, "Exit", "Exit")
        self.letters_coords_list.append(exit_button_coords)

        empty_label2 = Label(size_hint=(.05, 1 / 12), pos_hint={'y': 8 / 9, 'x': 0.95}, markup=True)
        self.add_widget(empty_label)
        self.add_widget(self.eye_label)
        self.add_widget(wifi_label)
        self.add_widget(exit_button)
        self.add_widget(empty_label2)
        
    def add_pick_intervals(self, margin):
        border = margin/4
        margin = 3*margin/2
        left = Button(background_color=(.3, .6, .7, 1), text = "1 сек",
                      size_hint=(.05, 1 / 12), 
                      pos_hint={'y': 7 / 8, 'x': margin}, font_size = 20
                      )
        left_interval =  LetterCoords(left, margin, 1 - (7/8 +  1 / 12), .05, 1/12, "", "interval_1")
        self.letters_coords_list.append(left_interval)
        self.intervals_list.append(left_interval)
        self.add_widget(left)
        
        
        margin = margin + .05 + border
        middle = Button(background_color=(.3, .6, .9, 1), text = "2 сек",
                      size_hint=(.05, 1 / 12), 
                      pos_hint={'y': 7 / 8, 'x': margin}, font_size = 20
                      )
        middle_interval =  LetterCoords(middle, margin, 1 - (7/8 +  1 / 12), .05, 1/12, "", "interval_2")
        self.letters_coords_list.append(middle_interval)
        self.intervals_list.append(middle_interval)
        self.add_widget(middle)
        
        margin = margin + .05 + border
        right = Button(background_color=(.3, .6, .7, 1), text = "3 сек",
                      size_hint=(.05, 1 / 12), 
                      pos_hint={'y': 7 / 8, 'x': margin}, font_size = 20
                      )
        self.add_widget(right)
        right_interval =  LetterCoords(right, margin, 1 - (7/8 +  1 / 12), .05, 1/12, "", "interval_3")
        self.letters_coords_list.append(right_interval)
        self.intervals_list.append(right_interval)

    def add_previous_text_labels(self, size_hint_x, margin, submit_y, submit_y_size):
        self.previous_text_labels = []
        margin = margin + size_hint_x / 2 + size_hint_x - size_hint_x / 3
        size_x = size_hint_x * 3 + size_hint_x / 2
        size_y = submit_y_size / 3.5
        label1 = SpecialLabel(size_hint=(size_x, size_y), pos_hint={'y': submit_y, 'x': margin},
                              font_size = 20,
                              text="Нема података"
                              )
        label1_coords = LetterCoords(label1, margin, 1 - (submit_y + size_y), size_x, size_y, "", "previous_text1")
        self.letters_coords_list.append(label1_coords)
        self.previous_text_labels.append(label1_coords)
        self.add_widget(label1)

        y_size = submit_y + submit_y_size / 3 + submit_y / 8
        label2 = SpecialLabel(size_hint=(size_x, size_y), pos_hint={'y': y_size, 'x': margin},
                              font_size = 20,
                               text="Нема података"
                              )
        self.add_widget(label2)
        label2_coords = LetterCoords(label2, margin, 1 - (y_size + size_y), size_x, size_y, "", "previous_text2")
        self.letters_coords_list.append(label2_coords)
        self.previous_text_labels.append(label2_coords)

        y_size = y_size + submit_y_size / 3 + submit_y / 8
        label3 = SpecialLabel(size_hint=(size_x, size_y), pos_hint={'y': y_size, 'x': margin},
                              font_size = 20,
                              text="Нема података"
                              )
        self.add_widget(label3)
        label3_coords = LetterCoords(label3, margin, 1 - (y_size + size_y), size_x, size_y, "", "previous_text3")
        self.letters_coords_list.append(label3_coords)
        self.previous_text_labels.append(label3_coords)