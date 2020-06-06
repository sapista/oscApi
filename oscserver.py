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
import oscrecvdsignals
import liblo

class OSCServer(liblo.ServerThread):
    def __init__(self, osc_port):
        self.OSCSignals = oscrecvdsignals.OSCReceiveSignals()
        liblo.ServerThread.__init__(self, osc_port)
        self.add_method("/strip/fader", 'if', self.fader_callback)
        self.add_method("/strip/solo", 'if', self.solo_callback)
        self.add_method("/strip/mute", 'if', self.mute_callback)
        self.add_method("/strip/recenable", 'if', self.rec_callback)
        self.add_method("/strip/select", 'if', self.select_callback)
        self.add_method("/strip/meter", 'if', self.meter_callback)
        self.add_method("/reply", 'ssiiiiii', self.reply_callback_Track)
        self.add_method("/reply", 'ssiiiii', self.reply_callback_Bus)
        self.add_method("/reply", 'shhi', self.reply_callback_EndRoute)
        self.add_method("/position/smpte", 's', self.smpte_position_callback)
        #self.add_method(None, None, self.fallback) #TODO enable this line only for debuging

    def fader_callback(self, path, args):
        i, f = args
        self.OSCSignals.emit_fader_changed(i, f)

    def solo_callback(self, path, args):
        i, f = args
        self.OSCSignals.emit_solo_changed(i, f > 0.5)

    def mute_callback(self, path, args):
        i, f = args
        self.OSCSignals.emit_mute_changed(i, f > 0.5)

    def rec_callback(self, path, args):
        i, f = args
        self.OSCSignals.emit_rec_changed(i, f > 0.5)

    def select_callback(self, path, args):
        i, f = args
        self.OSCSignals.emit_select_changed(i, f > 0.5)

    def meter_callback(self, path, args):
        i, f = args
        self.OSCSignals.emit_meter_changed(i, f)

    def reply_callback_Track(self, path, args):
        sstriptype, sstripname, inumins, inumouts, imute, isolo, issid, irec = args
        self.OSCSignals.emit_list_reply_track(issid, sstripname, stripselwidget.StripEnum().map_ardour_type(sstriptype),
                                              imute, isolo, irec, inumins, inumouts)

    def reply_callback_Bus(self, path, args):
        sstriptype, sstripname, inumins, inumouts, imute, isolo, issid = args
        self.OSCSignals.emit_list_reply_bus(issid, sstripname,
                                              stripselwidget.StripEnum().map_ardour_type(sstriptype),
                                              imute, isolo, inumins, inumouts)

    def reply_callback_EndRoute(self, path, args):
        sendroute, framerate, lastframenum, monitorsection = args
        if sendroute == "end_route_list":
            self.OSCSignals.emit_list_reply_end()

    def smpte_position_callback(self, path, args):
        self.OSCSignals.emit_smpte_changed(args)

    def fallback(self, path, args, types, src):
          str_types = ""
          str_args = ""
          for a, t in zip(args, types):
              str_types = str_types + "%s" % t
              str_args = str_args + "'%s'" % a + " "
          print(("received unknown message: %s " % path) + str_types + " " + str_args)
