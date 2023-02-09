from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.lang import Builder

Builder.load_string(

    '''<RoundedButton>
    background_color: (0, 0, 0, 0)
    background_normal: ''
    canvas.before:
        Color:
            rgba: (.3, .6, .7, .5)
        RoundedRectangle:
            size:self.size
            pos:self.pos
            radius: [80]'''
)

Builder.load_string(
            
                '''<SpecialLabel>
    background_color: (0, 0, 0, 0)
    background_normal: ''
    canvas.before:
        Color:
            rgba: (.3, .6, .7, .5)
        RoundedRectangle:
            size:self.size
            pos:self.pos
            radius: [30]'''
            
)

Builder.load_string(

    '''<ButtonWithBorder>
    background_color: (0, 0, 0, 0)

    canvas.before:
        Color:
            rgba: (0, 0, 0, 1)
        RoundedRectangle:
            size:self.size
            pos:self.pos
            radius: [350]
        Line:
            width: 5
            rectangle: self.x, self.y, self.width, self.height
             '''
)

class RoundedButton(Button):
    pass

class SpecialLabel(Button):
    pass

class ButtonWithBorder(Button):
    pass