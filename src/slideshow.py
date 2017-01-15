''' tk_image_slideshow3.py
create a Tkinter image repeating slide show
tested with Python27/33  by  vegaseat  03dec2013
'''

IMAGES= "images/*.png"
SOUND = "audio/g.wav"
import CHIP_IO.GPIO as GPIO
import glob
import pygame
from itertools import cycle
import Tkinter as tk
class App(tk.Tk):
    
    
    root = Tk()

# make it cover the entire screen
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w, h))



    '''Tk window/label adjusts to size of image'''
    def __init__(self,  x, y, delay):

        # the root will be self
        tk.Tk.__init__(self)

        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.overrideredirect(1)
        self.geometry("%dx%d+0+0" % (w, h))

        
        self.images = glob.glob(IMAGES);
        
        # set x, y position only
#         self.geometry('+{}+{}'.format(x, y))
        self.delay = delay
        # allows repeat cycling through the pictures
        # store as (img_object, img_name) tuple
        self.pictures = cycle((tk.PhotoImage(file=image), image)
                              for image in self.images)
        self.picture_display = tk.Label(self)
        self.picture_display.pack()
        
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(SOUND);
        
    def show_slides(self):
        '''cycle through the images and show them'''
        # next works with Python26 or higher
        img_object, img_name = next(self.pictures)
        self.gun_sound()
        self.picture_display.config(image=img_object)
        # shows the image filename, but could be expanded
        # to show an associated description of the image
        self.title(img_name)
        self.after(self.delay, self.show_slides)
        
    def run(self):
        self.mainloop()
        
    
    def gun_sound(self):
        pygame.mixer.music.play()
            
# set milliseconds time between slides
delay = 5000
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