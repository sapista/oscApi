"""
Definition of a widget to handle all Ardour controls of a single strip.
8 widgets of this class will be layout horizontally to represent the current selected bank.
This class is responsible to deal with all events related with SPI or I2C fader controller.
"""

import gtk
import gobject
import stripselwidget
import simplebuttonwidget

class StripCtlWidget(gtk.Frame):
    __gsignals__ = {
        'strip_selected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                           (gobject.TYPE_INT,)),

        'solo_changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                           (gobject.TYPE_INT, gobject.TYPE_BOOLEAN)),

        'mute_changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                         (gobject.TYPE_INT, gobject.TYPE_BOOLEAN)),

        'rec_changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                         (gobject.TYPE_INT, gobject.TYPE_BOOLEAN)),

        'fader_changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                         (gobject.TYPE_INT, gobject.TYPE_FLOAT))
    }

    def __init__(self):
        super(StripCtlWidget, self).__init__("")
        self.ssid = None
        self.stripname = ""
        self.type = None
        self.select = False
        self.solo = False
        self.mute = False
        self.rec = False

        self.vbox = gtk.VBox()
        self.lbl_strip_type = gtk.Label()
        self.vbox.pack_start(self.lbl_strip_type)
        self.table_selrecsolomute = gtk.Table(rows=2, columns=2, homogeneous=True)
        self.vbox.pack_start(self.table_selrecsolomute)

        # TODO molaria fer un boto jo amb el drawing area pq tingui un marc del color adequat i poder contorlar millor
        self.btn_select = simplebuttonwidget.SimpleButton("SEL", "#TODO")
        self.table_selrecsolomute.attach(self.btn_select, left_attach=0, right_attach=1, top_attach=0, bottom_attach=1,
                                            xoptions=gtk.EXPAND | gtk.FILL, yoptions=gtk.EXPAND)
        self.btn_rec = simplebuttonwidget.SimpleButton("REC", "#TODO")
        self.table_selrecsolomute.attach(self.btn_rec, left_attach=1, right_attach=2, top_attach=0, bottom_attach=1,
                                         xoptions=gtk.EXPAND | gtk.FILL, yoptions=gtk.EXPAND)
        self.btn_solo = simplebuttonwidget.SimpleButton("SOLO", "#TODO")
        self.table_selrecsolomute.attach(self.btn_solo, left_attach=0, right_attach=1, top_attach=1, bottom_attach=2,
                                            xoptions=gtk.EXPAND | gtk.FILL, yoptions=gtk.EXPAND)
        self.btn_mute = simplebuttonwidget.SimpleButton("MUTE", "#TODO")
        self.table_selrecsolomute.attach(self.btn_mute, left_attach=1, right_attach=2, top_attach=1, bottom_attach=2,
                                         xoptions=gtk.EXPAND | gtk.FILL, yoptions=gtk.EXPAND)

        self.add(self.vbox)
        self.set_border_width(2)

        self.btn_select.connect("clicked", self.select_clicked, None)
        self.btn_solo.connect("clicked", self.solo_clicked, None)
        self.btn_mute.connect("clicked", self.mute_clicked, None)
        self.btn_rec.connect("clicked", self.rec_clicked, None)

    def set_ssid_name(self, ssid, name):
        self.ssid = ssid
        self.stripname = name
        self.get_label_widget().set_markup("<span weight='bold' size='medium'>" + str(self.ssid) + "-" + self.stripname + "</span>")

    def set_strip_type(self, itype):
        self.type = itype
        # Set strip type label
        dirstriptype = {stripselwidget.StripEnum.AudioTrack: 'Audio Track',
                        stripselwidget.StripEnum.AudioBus: 'Audio Bus',
                        stripselwidget.StripEnum.MidiTrack: 'Midi Track',
                        stripselwidget.StripEnum.MidiBus: 'Midi Bus',
                        stripselwidget.StripEnum.AuxBus: 'Aux Bus',
                        stripselwidget.StripEnum.VCA: 'VCA'}
        self.lbl_strip_type.set_label(dirstriptype[self.type])
        if (self.type is stripselwidget.StripEnum.AudioTrack) or (self.type is stripselwidget.StripEnum.MidiTrack):
            self.btn_rec.show()
        else:
            self.btn_rec.hide()

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

    def select_clicked(self, widget, data = None):
        self.emit('strip_selected', self.ssid)

    def solo_clicked(self, widget, data=None):
        self.solo = not self.solo
        self.emit('solo_changed', self.ssid, self.solo)

    def mute_clicked(self, widget, data=None):
        self.mute = not self.mute
        self.emit('mute_changed', self.ssid, self.mute)

    def rec_clicked(self, widget, data=None):
        self.rec = not self.rec
        self.emit('rec_changed', self.ssid, self.rec)