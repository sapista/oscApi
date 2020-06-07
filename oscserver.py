""" OSCServer Class
This class uses the liblo.ServerThread to receive osc messages in an independent thread.
When an OSC message is received, it is parsed and the correct function of OSCReceiveSignals called.
This models ensures a thread-safe gtk signal generation for incoming osc messages
"""

""" Example of OSC debuging using liblo send_osc and dump_osc
1. Open two terminals
2. In the receiver terminal: dump_osc 8000
3. In the send terminal: send_osc osc.udp://127.0.0.1:3819 /strip/list
"""

import stripselwidget
import liblo
from gi.repository import GObject


class OSCServer(GObject.GObject):
    __gsignals__ = {
        'list_reply_track': (GObject.SIGNAL_RUN_LAST, None,
                             (int, str, int,  # ssid, name, type
                              bool, bool, bool,  # mute, solo, rec
                              int, int)),  # inputs, outputs

        'list_reply_bus': (GObject.SIGNAL_RUN_LAST, None,
                           (int, str, int,  # ssid, name, type
                            bool, bool,  # mute, solo
                            int, int)),  # inputs, outputs

        'list_reply_end': (GObject.SIGNAL_RUN_LAST, None,
                           ()),

        'fader_changed': (GObject.SIGNAL_RUN_LAST, None,
                          (int, float)),

        'solo_changed': (GObject.SIGNAL_RUN_LAST, None,
                         (int, bool)),

        'mute_changed': (GObject.SIGNAL_RUN_LAST, None,
                         (int, bool)),

        'rec_changed': (GObject.SIGNAL_RUN_LAST, None,
                        (int, bool)),

        'select_changed': (GObject.SIGNAL_RUN_LAST, None,
                           (int, bool)),

        'meter_changed': (GObject.SIGNAL_RUN_LAST, None,
                          (int, float)),

        'smpte_changed': (GObject.SIGNAL_RUN_LAST, None,
                          (str,)),

        'unknown_message': (GObject.SIGNAL_RUN_LAST, None,
                            (str,))

    }

    def __init__(self, osc_port):
        GObject.GObject.__init__(self)
        self.OSCReceiver = liblo.ServerThread(osc_port)
        self.OSCReceiver.add_method("/strip/fader", 'if', self.fader_callback)
        self.OSCReceiver.add_method("/strip/solo", 'if', self.solo_callback)
        self.OSCReceiver.add_method("/strip/mute", 'if', self.mute_callback)
        self.OSCReceiver.add_method("/strip/recenable", 'if', self.rec_callback)
        self.OSCReceiver.add_method("/strip/select", 'if', self.select_callback)
        self.OSCReceiver.add_method("/strip/meter", 'if', self.meter_callback)
        self.OSCReceiver.add_method("/reply", 'ssiiiiii', self.reply_callback_Track)
        self.OSCReceiver.add_method("/reply", 'ssiiiii', self.reply_callback_Bus)
        self.OSCReceiver.add_method("/reply", 'shhi', self.reply_callback_EndRoute)
        self.OSCReceiver.add_method("/position/smpte", 's', self.smpte_position_callback)
        self.OSCReceiver.add_method(None, None, self.fallback)

    def start(self):
        self.OSCReceiver.start()

    def stop(self):
        self.OSCReceiver.stop()

    def fader_callback(self, path, args):
        i, f = args
        GObject.idle_add(self.emit, 'fader_changed', i, f)

    def solo_callback(self, path, args):
        i, f = args
        GObject.idle_add(self.emit, 'solo_changed', i, f)

    def mute_callback(self, path, args):
        i, f = args
        GObject.idle_add(self.emit, 'mute_changed', i, f)

    def rec_callback(self, path, args):
        i, f = args
        GObject.idle_add(self.emit, 'rec_changed', i, f)

    def select_callback(self, path, args):
        i, f = args
        GObject.idle_add(self.emit, 'select_changed', i, f)

    def meter_callback(self, path, args):
        i, f = args
        GObject.idle_add(self.emit, 'meter_changed', i, f)

    def reply_callback_Track(self, path, args):
        sstriptype, sstripname, inumins, inumouts, imute, isolo, issid, irec = args
        GObject.idle_add(self.emit, 'list_reply_track',
                         issid, sstripname,
                         stripselwidget.StripEnum().map_ardour_type(sstriptype),
                         imute, isolo, irec, inumins, inumouts)

    def reply_callback_Bus(self, path, args):
        sstriptype, sstripname, inumins, inumouts, imute, isolo, issid = args
        GObject.idle_add(self.emit, 'list_reply_bus',
                         issid, sstripname,
                         stripselwidget.StripEnum().map_ardour_type(sstriptype),
                         imute, isolo, inumins, inumouts)

    def reply_callback_EndRoute(self, path, args):
        sendroute, framerate, lastframenum, monitorsection = args
        if sendroute == "end_route_list":
            GObject.idle_add(self.emit, 'list_reply_end')

    def smpte_position_callback(self, path, args):
        GObject.idle_add(self.emit, 'smpte_changed', args)

    def fallback(self, path, args, types, src):
        str_types = ""
        str_args = ""
        for a, t in zip(args, types):
            str_types = str_types + "%s" % t
            str_args = str_args + "'%s'" % a + " "
        GObject.idle_add(self.emit, 'unknown_message', ("received unknown message: %s " % path) + str_types + " " + str_args)
