"""
Definition of a widget to handle all Ardour controls of a single strip.
8 widgets of this class will be layout horizontally to represent the current selected bank.
This class is responsible to deal with all events related with SPI or I2C fader controller.
"""

from gi.repository import Gtk, GObject
from stripTypes import StripEnum
import simplebuttonwidget

MAX_TRACK_NAME_LENGTH = 10

class StripCtlWidget(Gtk.Frame):
    __gsignals__ = {
        'strip_selected': (GObject.SIGNAL_RUN_LAST, None,
                           (int, bool)),

        'solo_changed': (GObject.SIGNAL_RUN_LAST, None,
                         (int, bool)),

        'mute_changed': (GObject.SIGNAL_RUN_LAST, None,
                         (int, bool)),

        'rec_changed': (GObject.SIGNAL_RUN_LAST, None,
                        (int, bool)),

        'fader_changed': (GObject.SIGNAL_RUN_LAST, None,
                          (int, float))
    }

    def __init__(self):
        super(StripCtlWidget, self).__init__()
        #self.ssid = None
        #self.stripname = ""
        #self.type = None
        self.select = False
        self.solo = False
        self.mute = False
        self.rec = False
        self.set_label("") #start with an empty label

        self.vbox = Gtk.VBox()
        self.lbl_strip_type = Gtk.Label()
        self.vbox.pack_start(self.lbl_strip_type, expand=True, fill=True, padding=0)
        self.table_selrecsolomute = Gtk.Grid()
        self.vbox.pack_start(self.table_selrecsolomute, expand=True, fill=True, padding=0)

        self.btn_edit = Gtk.Button.new_with_label("Edit")
        self.table_selrecsolomute.attach(self.btn_edit, 0, 0, 2, 1)
        self.btn_select = simplebuttonwidget.SimpleButton("SEL", "#FF9023")
        self.table_selrecsolomute.attach(self.btn_select, 0, 1, 1, 1)
        self.btn_rec = simplebuttonwidget.SimpleButton("REC", "#FF0000")
        self.table_selrecsolomute.attach(self.btn_rec, 1, 1, 1, 1)
        self.btn_solo = simplebuttonwidget.SimpleButton("SOLO", "#00FF00")
        self.table_selrecsolomute.attach(self.btn_solo, 0, 2, 1, 1)
        self.btn_mute = simplebuttonwidget.SimpleButton("MUTE", "#FFFF00")
        self.table_selrecsolomute.attach(self.btn_mute, 1, 2, 1, 1)

        self.add(self.vbox)
        self.set_border_width(2)

        self.btn_select.connect("clicked", self.select_clicked, None)
        self.btn_solo.connect("clicked", self.solo_clicked, None)
        self.btn_mute.connect("clicked", self.mute_clicked, None)
        self.btn_rec.connect("clicked", self.rec_clicked, None)

        self.set_ssid_name(None, "")
        self.set_strip_type(StripEnum.Empty)

        self.set_size_request(-1, 120)

    def set_ssid_name(self, ssid, name):
        self.ssid = ssid
        if len(name) > MAX_TRACK_NAME_LENGTH:
            self.stripname = name[:MAX_TRACK_NAME_LENGTH] + "..."
        else:
            self.stripname = name
        if ssid is None:
            self.get_label_widget().set_markup("")
        else:
            self.get_label_widget().set_markup(
           "    <span weight='bold' size='medium'>" + str(self.ssid) + "-" + self.stripname + "</span>")

    def set_strip_type(self, itype):
        self.type = itype
        # Set strip type label
        dirstriptype = {StripEnum.Empty: '',
                        StripEnum.AudioTrack: 'Audio Track',
                        StripEnum.AudioBus: 'Audio Bus',
                        StripEnum.MidiTrack: 'Midi Track',
                        StripEnum.MidiBus: 'Midi Bus',
                        StripEnum.AuxBus: 'Aux Bus',
                        StripEnum.VCA: 'VCA'}
        self.lbl_strip_type.set_label(dirstriptype[self.type])
        if (self.type is StripEnum.AudioTrack) or (self.type is StripEnum.MidiTrack):
            self.btn_rec.show()
        else:
            self.btn_rec.hide()

        if self.type is StripEnum.Empty:
            self.btn_select.hide()
            self.btn_mute.hide()
            self.btn_solo.hide()
            self.btn_edit.hide()
        else:
            self.btn_select.show()
            self.btn_mute.show()
            self.btn_solo.show()
            self.btn_edit.show()

    def set_select(self, bvalue):
        self.select = bvalue
        self.btn_select.set_active_state(self.select)

    def set_solo(self, bvalue):
        self.solo = bvalue
        self.btn_solo.set_active_state(self.solo)

    def set_mute(self, bvalue):
        self.mute = bvalue
        self.btn_mute.set_active_state(self.mute)

    def set_rec(self, bvalue):
        self.rec = bvalue
        self.btn_rec.set_active_state(self.rec)

    def select_clicked(self, widget, data=None):
        self.select = not self.select
        self.emit('strip_selected', self.ssid, self.select)

    def solo_clicked(self, widget, data=None):
        self.solo = not self.solo
        self.emit('solo_changed', self.ssid, self.solo)

    def mute_clicked(self, widget, data=None):
        self.mute = not self.mute
        self.emit('mute_changed', self.ssid, self.mute)

    def rec_clicked(self, widget, data=None):
        self.rec = not self.rec
        self.emit('rec_changed', self.ssid, self.rec)

    def get_ssid(self):
        return self.ssid
