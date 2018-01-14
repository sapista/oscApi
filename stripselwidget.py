"""
Definition of a widget to handle a Ardour strip in a gtk table position.
The widget consists in 
  - a label with the name of the Ardour strip
  - a label with the strip type (audio track, audio bus, midi track, midi bus, VCA ...)
  - Three labels to indicate the state of solo, mute and record
  - a button with the background color corresponding to Ardour strip color. The button is also used for strip selection.
This widget stores all the information of each strip.
"""

import gtk
import gobject

class StripEnum:
    AudioTrack, MidiTrack, AudioBus, MidiBus, AuxBus, VCA = range(6)

    def __init__(self):
        self.ardourtypes = {'AT': self.AudioTrack, 'MT': self.MidiTrack, 'B': self.AudioBus, 'MB': self.MidiBus, 'AX': self.AuxBus, 'V':self.VCA}

    def map_ardour_type(self, sardourtype):
        return( self.ardourtypes[sardourtype])


class StripSelWidget(gtk.Frame):
    __gsignals__ = {
        'strip_selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                           (gobject.TYPE_INT, gobject.TYPE_INT))
    }

    def __init__(self, index, issid, ibank, sstripname, istriptype, mute, solo, inputs, outputs, rec=None):
        super(StripSelWidget, self).__init__(issid)
        self.index = index
        self.ssid = issid
        self.ibank = ibank
        self.stripname = sstripname
        self.lbl_name = gtk.Label()
        self.lbl_name.set_markup("<span weight='bold' size='medium'>" + self.stripname + "</span>")
        self.type = istriptype
        self.mute = mute
        self.solo = solo
        if (self.type is StripEnum.AudioTrack) or (self.type is StripEnum.MidiTrack):
            self.rec = rec
        self.inputs = inputs
        self.outputs = outputs



        # Set strip type label
        dirstriptype = {StripEnum.AudioTrack: 'Audio Track',
                        StripEnum.AudioBus: 'Audio Bus',
                        StripEnum.MidiTrack: 'Midi Track',
                        StripEnum.MidiBus: 'Midi Bus',
                        StripEnum.AuxBus: 'Aux Bus',
                        StripEnum.VCA: 'VCA'}

        self.lbl_type = gtk.Label()
        self.lbl_type.set_markup("<span size='small'>" + dirstriptype[istriptype] + "</span>")
        self.btn_sel = gtk.Button("")

        #Solo, mute rec labels
        self.hbox_smr = gtk.HBox()
        self.lbl_solo = gtk.Label()
        self.hbox_smr.pack_start(self.lbl_solo)
        self.set_solo(self.solo)
        self.lbl_mute = gtk.Label()
        self.hbox_smr.pack_start(self.lbl_mute)
        self.set_mute(self.mute)
        if (self.type is StripEnum.AudioTrack) or (self.type is StripEnum.MidiTrack):
            self.lbl_rec = gtk.Label()
            self.hbox_smr.pack_start(self.lbl_rec)
            self.set_rec(self.rec)

        self.vbox = gtk.VBox()
        self.vbox.pack_start(self.lbl_name)
        self.vbox.pack_start(self.lbl_type)
        self.vbox.pack_start(self.hbox_smr)
        self.vbox.pack_start(self.btn_sel)
        self.add(self.vbox)
        self.set_border_width(2)
        self.btn_sel.connect("clicked", self.btn_clicked, None)

        self.selected = False

    def btn_clicked(self, widget, data=None):
        self.emit('strip_selected', self.ssid, self.ibank)

    def get_index(self):
        return self.index

    def get_ssid(self):
        return self.ssid

    def get_bank(self):
        return self.ibank

    def set_selected(self, select):
        self.selected = select
        if self.selected:
            self.lbl_name.set_markup("<span foreground='red' weight='bold' size='medium'>" + self.stripname + "</span>")
        else:
            self.lbl_name.set_markup("<span weight='bold' size='medium'>" + self.stripname + "</span>")

    def get_selected(self):
        return self.selected

    def set_solo(self, bvalue):
        self.solo = bvalue
        if self.solo:
            self.lbl_solo.set_markup("<span background='#00FF00FF' size='small'>solo</span>")
        else:
            self.lbl_solo.set_markup("<span size='small'>solo</span>")

    def set_mute(self, bvalue):
        self.mute = bvalue
        if self.mute:
            self.lbl_mute.set_markup("<span background='#FFFF00FF' size='small'>mute</span>")
        else:
            self.lbl_mute.set_markup("<span size='small'>mute</span>")

    def set_rec(self, bvalue):
        if (self.type is StripEnum.AudioTrack) or (self.type is StripEnum.MidiTrack):
            self.rec = bvalue
            if self.rec:
                self.lbl_rec.set_markup("<span background='#FF0000FF' size='small'>rec</span>")
            else:
                self.lbl_rec.set_markup("<span size='small'>rec</span>")
