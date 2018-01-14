""" OSCReceiveSignals Class
This class declares every used osc messaged generated by Ardour and able to be parsed by this controller.
This class must be only used by OSCServer class.
This class provides an emit function for each recived OSC message.
Each emit is wrapped around gobject.idle_add() for thread safety.
"""

import gobject


class OSCReceiveSignals(gobject.GObject):
    __gsignals__ = {
        'list_reply_track': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          (gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_INT, # ssid, name, type
                           gobject.TYPE_BOOLEAN, gobject.TYPE_BOOLEAN, gobject.TYPE_BOOLEAN, # mute, solo, rec
                           gobject.TYPE_INT, gobject.TYPE_INT)), # inputs, outputs

        'list_reply_bus': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                             (gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_INT, # ssid, name, type
                              gobject.TYPE_BOOLEAN, gobject.TYPE_BOOLEAN, # mute, solo
                              gobject.TYPE_INT, gobject.TYPE_INT)), # inputs, outputs

        'list_reply_end': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                           ()),

        'fader_changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          (gobject.TYPE_INT, gobject.TYPE_FLOAT)),

        'solo_changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                        (gobject.TYPE_INT, gobject.TYPE_BOOLEAN)),

        'mute_changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                         (gobject.TYPE_INT, gobject.TYPE_BOOLEAN)),

        'rec_changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                         (gobject.TYPE_INT, gobject.TYPE_BOOLEAN)),

        'select_changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                          (gobject.TYPE_INT, gobject.TYPE_BOOLEAN))
    }

    def __init__(self):
        gobject.GObject.__init__(self)

    def emit_list_reply_track(self, ichannel, sname, itype, bmute, bsolo, brec, iinputs, ioutputs):
        gobject.idle_add(self.emit, 'list_reply_track', ichannel, sname, itype, bmute, bsolo, brec, iinputs, ioutputs)

    def emit_list_reply_bus(self, ichannel, sname, itype, bmute, bsolo, iinputs, ioutputs):
        gobject.idle_add(self.emit, 'list_reply_bus', ichannel, sname, itype, bmute, bsolo, iinputs, ioutputs)

    def emit_list_reply_end(self):
        gobject.idle_add(self.emit, 'list_reply_end')

    def emit_fader_changed(self, ichannel, fvalue):
        gobject.idle_add(self.emit, 'fader_changed', ichannel, fvalue)

    def emit_solo_changed(self, ichannel, bvalue):
        gobject.idle_add(self.emit, 'solo_changed', ichannel, bvalue)

    def emit_mute_changed(self, ichannel, bvalue):
        gobject.idle_add(self.emit, 'mute_changed', ichannel, bvalue)

    def emit_rec_changed(self, ichannel, bvalue):
        gobject.idle_add(self.emit, 'rec_changed', ichannel, bvalue)

    def emit_select_changed(self, ichannel, bselected):
        gobject.idle_add(self.emit, 'select_changed', ichannel, bselected)