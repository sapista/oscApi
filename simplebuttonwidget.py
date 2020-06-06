"""
Definition of a two-state simple button able to handle ardour LED state and send ardour button booleans.
"""

from gi.repository import Gtk, GObject, Gdk
import math
import cairo
import colorsys


class SimpleButton(Gtk.EventBox):
    __gsignals__ = {
        'clicked': (GObject.SIGNAL_RUN_LAST, None, ())
    }

    def __init__(self, text, color):
        super(SimpleButton, self).__init__()
        self.active_state = False
        self.label = text
        self.color_active = Gdk.RGBA()
        self.color_active.parse(color)
        hsvColor = colorsys.rgb_to_hsv(self.color_active.red, self.color_active.green, self.color_active.blue)
        rgbColor = colorsys.hsv_to_rgb(hsvColor[0], hsvColor[1] * 0.4, hsvColor[2] * 0.5)
        self.color_inactive = Gdk.RGBA()
        self.color_inactive.red = rgbColor[0]
        self.color_inactive.green = rgbColor[1]
        self.color_inactive.blue = rgbColor[2]
        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.on_draw)
        self.add(self.darea)
        self.set_size_request(60, 40)

        # And bind an action to it
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.button_press)

    def button_press(self, widget, event):
        if event.button == 1:
            self.emit("clicked")

    def set_active_state(self, bvalue):
        self.active_state = bvalue
        self.queue_draw()

    def on_draw(self, area, cr):
        w = area.get_allocated_width()
        h = area.get_allocated_height()
        border = 2
        radius = 5

        cr.set_line_width(2)
        cr.set_source_rgb(0.0, 0.0, 0.0)  # Color of the border line

        cr.arc(border + radius, border + radius, radius, math.pi, 3.0 * math.pi / 2.0)
        cr.line_to(w - border - radius, border)
        cr.arc(w - border - radius, border + radius, radius, 3.0 * math.pi / 2.0, 0.0)
        cr.line_to(w - border, h - border - radius)
        cr.arc(w - border - radius, h - border - radius, radius, 0.0, math.pi / 2.0)
        cr.line_to(border + radius, h - border)
        cr.arc(border + radius, h - border - radius, radius, math.pi / 2.0, math.pi)
        cr.close_path()
        cr.stroke_preserve()

        if self.active_state:
            cr.set_source_rgb(self.color_active.red, self.color_active.green, self.color_active.blue)
        else:
            cr.set_source_rgb(self.color_inactive.red, self.color_inactive.green, self.color_inactive.blue)
        cr.fill()

        cr.set_source_rgb(0.0, 0.0, 0.0)  # Color for the text
        cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)
        txt_x, txt_y, txt_w, txt_h, txt_dx, txt_dy = cr.text_extents(self.label)
        cr.move_to(w / 2.0 - txt_w / 2.0, h / 2.0 + txt_h / 2.0)
        cr.show_text(self.label)
