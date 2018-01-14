""" OSCServer Class
This class uses the liblo.ServerThread to receive osc messages in an independent thread.
When an OSC message is received, it is parsed and the correct function of OSCReceiveSignals called.
This models ensures a thread-safe gtk signal generation for incoming osc messages
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
        self.add_method(None, None, self.fallback)

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

    def reply_callback(self, path, args):
        ardour_maps = stripselwidget.StripEnum()
        if len(args) is 7:
            sstriptype, sstripname, inumins, inumouts, imute, isolo, issid = args

        elif len(args) is 8:
            sstriptype, sstripname, inumins, inumouts, imute, isolo, issid, irec = args

        elif len(args) is 4:
            sendroute, framerate, lastframenum, monitorsection = args
            if sendroute == "end_route_list":
                self.OSCSignals.emit_list_reply_end()
                return
        else:
            return

        istriptype = ardour_maps.map_ardour_type(sstriptype)
        if (istriptype is stripselwidget.StripEnum.AudioTrack) or (istriptype is stripselwidget.StripEnum.MidiTrack):
            self.OSCSignals.emit_list_reply_track(issid, sstripname, istriptype, imute > 0.5, isolo > 0.5, irec > 0.5, inumins, inumouts)
        else:
            self.OSCSignals.emit_list_reply_bus(issid, sstripname, istriptype, imute > 0.5, isolo > 0.5, inumins, inumouts)

    def fallback(self, path, args, types, src):
        # The #reply messages are not handled by liblo callback system.
        # So, I'm using the fallback method to handle those messages here.
         if path == "#reply":
            self.reply_callback(path, args)

         else:
            str_types = ""
            str_args = ""
            for a, t in zip(args, types):
                str_types = str_types + "%s" % t
                str_args = str_args + "'%s'" % a + " "
            print ("received unknown message: %s " % path) + str_types + " " + str_args