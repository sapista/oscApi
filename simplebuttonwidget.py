"""
Definition of a two-state simple button able to handle ardour LED state and send ardour button booleans.
"""

import gtk
import gobject
import math
import cairo


class SimpleButton(gtk.EventBox):
    __gsignals__ = {
        'clicked': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }

    def __init__(self, text, color):
        super(SimpleButton, self).__init__()
        self.active_state = False
        self.label = text
        self.color = color
        self.darea = gtk.DrawingArea()
        self.darea.connect("expose-event", self.expose)
        self.add(self.darea)
        self.set_size_request(80, 30)

        # And bind an action to it
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect("button_press_event", self.button_press)

    def button_press (self, widget, event):
        if event.button is 1:
            self.emit("clicked")

    def set_active_state(self, bvalue):
        self.active_state = bvalue
        self.queue_draw()

    def expose(self, widget, event):
        x, y, w, h = event.area
        border = 2
        radius = 5

        cr = widget.get_window().cairo_create()

        cr.set_line_width(2)
        cr.set_source_rgb(0.0, 0.0, 0.0) # Color of the border line

        cr.arc(border+radius, border+radius, radius, math.pi, 3.0 * math.pi / 2.0)
        cr.line_to(w - border - radius, border)
        cr.arc(w - border - radius, border + radius, radius, 3.0 * math.pi / 2.0, 0.0)
        cr.line_to(w - border, h - border - radius)
        cr.arc(w - border - radius, h - border - radius, radius, 0.0, math.pi / 2.0)
        cr.line_to(border+radius, h - border)
        cr.arc(border+radius, h - border - radius, radius, math.pi / 2.0, math.pi)
        cr.close_path()
        cr.stroke_preserve()

# TODO use the self.color param here!
        if self.active_state:
            cr.set_source_rgb(1.0, 1.0, 0.0) # Color of the button fill
        else:
            cr.set_source_rgb(0.8, 0.8, 0.0)  # Color of the button fill
        cr.fill()

        cr.set_source_rgb(0.0, 0.0, 0.0) # Color for the text
        cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)
        txt_x, txt_y, txt_w, txt_h, txt_dx, txt_dy = cr.text_extents(self.label)
        cr.move_to(w/2.0 - txt_w/2.0, h/2.0 + txt_h/2.0)
        cr.show_text(self.label)
