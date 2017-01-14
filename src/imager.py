'''
Created on Jan 14, 2017

@author: howie
'''


import glob
import time
from PIL import Image

IMAGES = "images/*.png"
IMAGES= "/home/howie/Pictures/*.*"

class Imager(object):
    def __init__(self):
        self.images = glob.glob(IMAGES);
        self.index = 0
        
    def run(self):
        while True:
            image = Image.open(self.images[self.index])
            image.show()
            self.index = (self.index + 1) % len(self.images)
            time.sleep(5);
            image.close();
            
        

if __name__ == '__main__':
    imager = Imager()
    imager.run();
