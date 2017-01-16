
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Taken and customed from Jack Valmadre's Blog:
# http://jackvalmadre.wordpress.com/2008/09/21/resizable-image-control/
#
# Put together and created the time switching by Izidor Matusov <izidor.matusov@gmail.com>

import os
import glob
import pygtk
pygtk.require('2.0')
import gtk
import glib
import pygame
import subprocess

SOUND = "audio/g.wav"
IMAGES= "images/*.png"


def is_image(filename):
    """ File is image if it has a common suffix and it is a regular file """
    return True
    if not os.path.isfile(filename):
        return False

    for suffix in ['.jpg', '.png', '.bmp']:
        if filename.lower().endswith(suffix):
            return True

    return False

def resizeToFit(image, frame, aspect=True, enlarge=False):
    """Resizes a rectangle to fit within another.

    Parameters:
    image -- A tuple of the original dimensions (width, height).
    frame -- A tuple of the target dimensions (width, height).
    aspect -- Maintain aspect ratio?
    enlarge -- Allow image to be scaled up?

    """
    if aspect:
        return scaleToFit(image, frame, enlarge)
    else:
        return stretchToFit(image, frame, enlarge)

def scaleToFit(image, frame, enlarge=False):
    image_width, image_height = image
    frame_width, frame_height = frame
    image_aspect = float(image_width) / image_height
    frame_aspect = float(frame_width) / frame_height
    # Determine maximum width/height (prevent up-scaling).
    if not enlarge:
        max_width = min(frame_width, image_width)
        max_height = min(frame_height, image_height)
    else:
        max_width = frame_width
        max_height = frame_height
    # Frame is wider than image.
    if frame_aspect > image_aspect:
        height = max_height
        width = int(height * image_aspect)
    # Frame is taller than image.
    else:
        width = max_width
        height = int(width / image_aspect)
    return (width, height)

def stretchToFit(image, frame, enlarge=False):
    image_width, image_height = image
    frame_width, frame_height = frame
    # Stop image from being blown up.
    if not enlarge:
        width = min(frame_width, image_width)
        height = min(frame_height, image_height)
    else:
        width = frame_width
        height = frame_height
    return (width, height)


class ResizableImage(gtk.DrawingArea):

    def __init__(self, aspect=True, enlarge=False,
            interp=gtk.gdk.INTERP_NEAREST, backcolor=None, max=(1600,1200)):
        """Construct a ResizableImage control.

        Parameters:
        aspect -- Maintain aspect ratio?
        enlarge -- Allow image to be scaled up?
        interp -- Method of interpolation to be used.
        backcolor -- Tuple (R, G, B) with values ranging from 0 to 1,
            or None for transparent.
        max -- Max dimensions for internal image (width, height).

        """
        super(ResizableImage, self).__init__()
        self.pixbuf = None
        self.aspect = aspect
        self.enlarge = enlarge
        self.interp = interp
        self.backcolor = backcolor
        self.max = max
        self.connect('expose_event', self.expose)
        self.connect('realize', self.on_realize)

    def on_realize(self, widget):
        if self.backcolor is None:
            color = gtk.gdk.Color()
        else:
            color = gtk.gdk.Color(*self.backcolor)

        self.window.set_background(color)

    def expose(self, widget, event):
        # Load Cairo drawing context.
        self.context = self.window.cairo_create()
        # Set a clip region.
        self.context.rectangle(
            event.area.x, event.area.y,
            event.area.width, event.area.height)
        self.context.clip()
        # Render image.
        self.draw(self.context)
        return False

    def draw(self, context):
        # Get dimensions.
        rect = self.get_allocation()
        x, y = rect.x, rect.y
        # Remove parent offset, if any.
        parent = self.get_parent()
        if parent:
            offset = parent.get_allocation()
            x -= offset.x
            y -= offset.y
        # Fill background color.
        if self.backcolor:
            context.rectangle(x, y, rect.width, rect.height)
            context.set_source_rgb(*self.backcolor)
            context.fill_preserve()
        # Check if there is an image.
        if not self.pixbuf:
            return
        width, height = resizeToFit(
            (self.pixbuf.get_width(), self.pixbuf.get_height()),
            (rect.width, rect.height),
            self.aspect,
            self.enlarge)
        x = x + (rect.width - width) / 2
        y = y + (rect.height - height) / 2
        context.set_source_pixbuf(
            self.pixbuf.scale_simple(width, height, self.interp), x, y)
        context.paint()

    def set_from_pixbuf(self, pixbuf):
        width, height = pixbuf.get_width(), pixbuf.get_height()
        # Limit size of internal pixbuf to increase speed.
        if not self.max or (width < self.max[0] and height < self.max[1]):
            self.pixbuf = pixbuf
        else:
            width, height = resizeToFit((width, height), self.max)
            self.pixbuf = pixbuf.scale_simple(
                width, height,
                gtk.gdk.INTERP_BILINEAR)
        self.invalidate()

    def set_from_file(self, filename):
        self.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(filename))

    def invalidate(self):
        self.queue_draw()

class SlideShow:

    FULLSCREEN = True
    WALK_INSTEAD_LISTDIR = False

    def __init__(self, queue, delay):
        self.queue = queue
        self.delay = delay
        print "slide show delay",self.delay
        self.window = gtk.Window()
        self.window.connect('destroy', gtk.main_quit)
        self.window.set_title('Slideshow')

        self.image = ResizableImage( True, True, gtk.gdk.INTERP_BILINEAR)
        self.image.show()
        
        ip =  subprocess.Popen("hostname -I", shell=True, stdout=subprocess.PIPE).stdout.read()
#         label = gtk.Label("<b>' + ip + 'abcdef</b>")
        label = gtk.Label()
        label.set_use_markup(True)
        
        label.set_markup('<span size="78000">' + ip + '</span>')
        self.label = label
#         label = gtk.Label("192.168.1.1:8080")
        self.window.add(label);
        
#         self.window.add(self.image)

        self.load_file_list()

        self.window.show_all()

        if self.FULLSCREEN:
            self.window.fullscreen()

        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(SOUND);

        self.timer = None
        self.set_tick_timeout()
        
        glib.idle_add(self.check_queue)
        self.display()

    def check_queue(self):
        try:
            item = self.queue.get_nowait()
            n = int(item)
            if n == -1:
                self.on_tick()
            else:
                self.delay = n
                self.set_tick_timeout()
        except KeyboardInterrupt:
            gtk.main_quit()
            raise
        except:
            pass
        return True
        
    def load_file_list(self):
        """ Find all images """
        self.files = []
        self.index = 0
        self.files = glob.glob(IMAGES);
        print "Images:", self.files

    def display(self):
        """ Sent a request to change picture if it is possible """
        if 0 <= self.index < len(self.files):
            self.image.set_from_file(self.files[self.index])
            return True
        else:
            return False
        
    def set_tick_timeout(self):
        if self.timer:
            glib.source_remove(self.timer)
        if self.delay > 0:
            self.timer = glib.timeout_add_seconds(self.delay, self.on_tick)

    def gun_sound(self):
        pygame.mixer.music.play()

    def on_tick(self):
        """ Skip to another picture.

        If this picture is last, go to the first one. """
        
        if self.label:
            self.window.remove(self.label)
            self.label = None
            self.window.add(self.image)

            
        self.index += 1
        if self.index >= len(self.files):
            self.index = 0
        self.gun_sound()
        self.display()
        self.set_tick_timeout()

if __name__ == "__main__":
    gui = SlideShow()
    gtk.main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4