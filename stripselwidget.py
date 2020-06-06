"""
Definition of a widget to handle a Ardour strip in a gtk table position.
The widget consists in 
  - a label with the name of the Ardour strip
  - a label with the strip type (audio track, audio bus, midi track, midi bus, VCA ...)
  - Three labels to indicate the state of solo, mute and record
  - a button with the background color corresponding to Ardour strip color. The button is also used for strip selection.
This widget stores all the information of each strip.
"""

from gi.repository import Gtk, GObject, Gdk
import customframewidget
import miniMeter
import LEDWidget
from stripTypes import StripEnum
MAX_TRACK_NAME_LENGTH = 15

class StripSelWidget(Gtk.EventBox):
    __gsignals__ = {
        'strip_selected': (GObject.SIGNAL_RUN_LAST, None,
                           (int, int))
    }

    def __init__(self, index, issid, ibank, sstripname, istriptype, mute, solo, inputs, outputs, rec=None):
        super(StripSelWidget, self).__init__()
        self.index = index
        self.ssid = issid
        self.ibank = ibank
        if len(sstripname) > MAX_TRACK_NAME_LENGTH:
            self.stripname = sstripname[:MAX_TRACK_NAME_LENGTH]  + "..."
        else:
            self.stripname = sstripname
        self.lbl_name = Gtk.Label()
        self.lbl_name.set_markup("<span weight='bold' size='medium'>" + str(self.ssid) + "-" + self.stripname + "</span>")
        self.type = istriptype
        self.MFrame = customframewidget.CustomFrame(self.type)
        self.inputs = inputs
        self.outputs = outputs

        # Set strip type label
        dirstriptype = {StripEnum.Empty: '',
                        StripEnum.AudioTrack: 'Audio Track',
                        StripEnum.AudioBus: 'Audio Bus',
                        StripEnum.MidiTrack: 'Midi Track',
                        StripEnum.MidiBus: 'Midi Bus',
                        StripEnum.AuxBus: 'Aux Bus',
                        StripEnum.VCA: 'VCA'}

        self.lbl_type = Gtk.Label()
        self.lbl_type.set_markup("<span size='small'>" + dirstriptype[istriptype] + "</span>")

        #Waveform viewer
        self.meter = miniMeter.MiniMeter()

        # Solo, mute rec labels
        self.hbox_smr = Gtk.HBox()
        self.LED_solo = LEDWidget.LEDWidget("Solo", "#00FF00")
        self.LED_solo.set_value(solo)
        self.hbox_smr.pack_start(self.LED_solo, expand=True, fill=True, padding=0)
        self.LED_mute = LEDWidget.LEDWidget("Mute", "#FFFF00")
        self.LED_mute.set_value(mute)
        self.hbox_smr.pack_start(self.LED_mute, expand=True, fill=True, padding=0)
        if (self.type is StripEnum.AudioTrack) or (self.type is StripEnum.MidiTrack):
            self.LED_rec = LEDWidget.LEDWidget("Rec", "#FF0000")
            self.LED_rec.set_value(rec)
            self.hbox_smr.pack_start(self.LED_rec, expand=True, fill=True, padding=0)

        self.vbox = Gtk.VBox()
        self.vbox.pack_start(self.lbl_name, expand=True, fill=True, padding=0)
        self.vbox.pack_start(self.lbl_type, expand=True, fill=True, padding=0)
        self.vbox.pack_start(self.meter, expand=True, fill=True, padding=0)
        self.vbox.pack_start(self.hbox_smr, expand=True, fill=True, padding=0)
        self.MFrame.add(self.vbox)
        self.add(self.MFrame)
        self.MFrame.set_border_width(2)

        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.button_press)

        self.selected = False

    def button_press(self, widget, event):
        if event.button == 1:
            self.emit('strip_selected', self.ssid, self.ibank)

    def get_index(self):
        return self.index

    def get_ssid(self):
        return self.ssid

    def get_bank(self):
        return self.ibank

    def set_selected(self, select):
        self.selected = select
        self.MFrame.set_selected(self.selected)
        if self.selected:
            self.lbl_name.set_markup("<span foreground='#00ffc8' weight='bold' size='medium'>" + str(self.ssid) + "-" + self.stripname + "</span>")
        else:
            self.lbl_name.set_markup("<span weight='bold' size='medium'>" + str(self.ssid) + "-" + self.stripname + "</span>")

    def set_bank_selected(self, bank_selected):
        self.MFrame.set_bank_selected(bank_selected)

    def get_selected(self):
        return self.selected

    def set_solo(self, bvalue):
        self.LED_solo.set_value(bvalue)

    def set_mute(self, bvalue):
        self.LED_mute.set_value(bvalue)

    def set_rec(self, bvalue):
        if (self.type is StripEnum.AudioTrack) or (self.type is StripEnum.MidiTrack):
            self.LED_rec.set_value(bvalue)

    def get_solo(self):
        return self.LED_solo.get_value()

    def get_mute(self):
        return self.LED_mute.get_value()

    def get_rec(self):
        if (self.type is StripEnum.AudioTrack) or (self.type is StripEnum.MidiTrack):
            return self.LED_rec.get_value()

    def set_meter(self, value):
        self.meter.set_value(value)

    def refresh_meter(self):
        self.meter.refresh()

