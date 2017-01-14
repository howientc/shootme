''' tk_image_slideshow3.py
create a Tkinter image repeating slide show
tested with Python27/33  by  vegaseat  03dec2013
'''

IMAGES= "images/*.png"
import glob
from itertools import cycle
import Tkinter as tk
class App(tk.Tk):
    '''Tk window/label adjusts to size of image'''
    def __init__(self,  x, y, delay):
        self.images = glob.glob(IMAGES);

        # the root will be self
        tk.Tk.__init__(self)
        # set x, y position only
        self.geometry('+{}+{}'.format(x, y))
        self.delay = delay
        # allows repeat cycling through the pictures
        # store as (img_object, img_name) tuple
        self.pictures = cycle((tk.PhotoImage(file=image), image)
                              for image in self.images)
        self.picture_display = tk.Label(self)
        self.picture_display.pack()
    def show_slides(self):
        '''cycle through the images and show them'''
        # next works with Python26 or higher
        img_object, img_name = next(self.pictures)
        self.picture_display.config(image=img_object)
        # shows the image filename, but could be expanded
        # to show an associated description of the image
        self.title(img_name)
        self.after(self.delay, self.show_slides)
    def run(self):
        self.mainloop()
# set milliseconds time between slides
delay = 3500
# get a series of gif images you have in the working folder
# or use full path, or set directory to where the images are
image_files = [
'Slide_Farm.gif',
'Slide_House.gif',
'Slide_Sunset.gif',
'Slide_Pond.gif',
'Slide_Python.gif'
]
# upper left corner coordinates of app window
x = 100
y = 50
app = App( x, y, delay)
app.show_slides()
app.run()