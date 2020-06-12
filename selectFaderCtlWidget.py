"""
A widget to handle fader state of the selected channel.
This widget can control the fader, trim gain and sends but not the stereo panner
This widgets includes automation state contorls
"""

from gi.repository import Gtk, GObject
import simplebuttonwidget
import customframewidget
from automationTypes import AutomationModes


class SelectFaderCtlWidget(customframewidget.CustomFrame):
    __gsignals__ = {
        'automation_changed': (GObject.SIGNAL_RUN_LAST, None,
                               (int,)),
    }

    def __init__(self, name):
        super(SelectFaderCtlWidget, self).__init__(0)

        self.vbox = Gtk.VBox()
        self.lbl_title = Gtk.Label()
        self.lbl_title.set_markup("<span weight='bold' font_desc='Arial 16'>" + name + "</span>")
        self.vbox.pack_start(self.lbl_title, expand=True, fill=True, padding=0)
        self.lbl_dBvalue = Gtk.Label()
        self.vbox.pack_start(self.lbl_dBvalue, expand=True, fill=True, padding=0)

        self.table_automationModes = Gtk.Grid()
        self.vbox.pack_start(self.table_automationModes, expand=True, fill=True, padding=0)

        self.btn_Manual = simplebuttonwidget.SimpleButton("Manual", "#E76626")
        self.table_automationModes.attach(self.btn_Manual, 0, 0, 2, 1)

        self.btn_Play = simplebuttonwidget.SimpleButton("Play", "#E76626")
        self.table_automationModes.attach(self.btn_Play, 0, 1, 1, 1)

        self.btn_Write = simplebuttonwidget.SimpleButton("Write", "#E76626")
        self.table_automationModes.attach(self.btn_Write, 1, 1, 1, 1)

        self.btn_Touch = simplebuttonwidget.SimpleButton("Touch", "#E76626")
        self.table_automationModes.attach(self.btn_Touch, 0, 2, 1, 1)

        self.btn_Latch = simplebuttonwidget.SimpleButton("Latch", "#E76626")
        self.table_automationModes.attach(self.btn_Latch, 1, 2, 1, 1)

        self.add(self.vbox)
        self.vbox.set_border_width(7)

        # TODO connect signals, implement callbakcs... etc!!!!!

    def set_gain_label(self, value):
        self.lbl_dBvalue.set_text(str(round(value, 2)) + " dB")
