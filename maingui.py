#!/usr/bin/env python

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

import liblo
import sys
import oscserver
import stripselwidget
import stripctlwidget
import math
import xml.etree.ElementTree as ET
import ast
import pyFaderSerialCOM


""" ControllerGUI class
This class implements a gtk GUI for sending osc messages using the liblo.send() method.
The GUI is also able to receive OSC messages in a signal-handler model using OSCServer class.
"""

#TODO, tot seguit un trucu k he trobat per internet per quan anem a release final potser cal pel path dels icones
#from os.path import abspath, dirname
#WHERE_AM_I = abspath(dirname(__file__))


class ControllerGUI(Gtk.Window):
    def delete_event(self, widget, event, data=None):
        quitDialog = Gtk.MessageDialog(parent=None,
                                       modal=True,
                                       message_type=Gtk.MessageType.QUESTION,
                                       buttons=Gtk.ButtonsType.YES_NO,
                                       text="Are you sure to quit?")

        resp = quitDialog.run()
        quitDialog.destroy()
        if resp == Gtk.ResponseType.YES:
            self.oscserver.stop()
            self.avrCOM.close()
            return False

        #Keep the application open
        return True

    def destroy(self, widget, data=None):
         Gtk.main_quit()

    def btn_test_clicked(self, widget, data=None):
        liblo.send(self.target, "/toggle_roll")

    def btn_playStop_clicked(self, widget, data=None):
        liblo.send(self.target, "/toggle_roll")

    def btn_loop_clicked(self, widget, data=None):
        liblo.send(self.target, "/loop_toggle")
        if self.bLooping:
            self.bLooping = False
            self.btn_loop.set_image(self.btn_loop_WhiteIcon)
        else:
            self.bLooping = True

    def fader_moved(self, event, channel, value):
        if len(self.strips_list_widgets) > 0: #Only if we have strip list from DAW
            selSSID = self.strips_list_selbank[channel].get_ssid()
            if selSSID is not None:
                liblo.send(self.target, "/strip/fader/touch", selSSID, 1)  # Using floats it works
                liblo.send(self.target, "/strip/fader", selSSID, value)
        return True

    def fader_untouched(self, event, value):
        if len(self.strips_list_widgets) > 0:  # Only if we have strip list from DAW
            #print("Unotuch event: %x", value)
            for i in range(0,8):
                if value & (1<<i):
                    selSSID = self.strips_list_selbank[i].get_ssid()
                    if selSSID is not None:
                        liblo.send(self.target, "/strip/fader/touch", selSSID, 0)
        return True

    def strip_selected(self, widget, issid, ibank, data=None):
        liblo.send(self.target, "/strip/select", issid, 1)

    def refresh_strip_list(self, widget, data=None):
        self.strips_list_widgets = []  # Clear the list
        self.strips_ssid_id_dict = dict()  # Clear the id ssid dictionary
        # Config the surface as infinite banks, track setting, strip feedback and fader as position values
        liblo.send(self.target, "/set_surface", 0, 7, 24771, 3, 0) #Check Ardour OSC preferences for reference of these values
            #the feedback value of 24771 includes the level meters as text and the changes the #reply messages to /reply
        liblo.send(self.target, "/strip/list")

    def refresh_bank_sel(self):
        for i in range(0, len(self.strips_list_selbank)):
            working_ssid = self.current_selected_bank * 8 + i + 1  # plus one because ardour indexes from 1
            if working_ssid in self.strips_ssid_id_dict:
                id = self.strips_ssid_id_dict[working_ssid]
                self.strips_list_selbank[i].set_ssid_name(working_ssid, self.strips_list_widgets[id].stripname)
                self.strips_list_selbank[i].set_strip_type(self.strips_list_widgets[id].type)
                self.strips_list_selbank[i].set_select(self.strips_list_widgets[id].get_selected())
                self.strips_list_selbank[i].set_solo(self.strips_list_widgets[id].get_solo())
                self.strips_list_selbank[i].set_mute(self.strips_list_widgets[id].get_mute())
                if (self.strips_list_widgets[id].type is stripselwidget.StripEnum.AudioTrack) or (
                        self.strips_list_widgets[id].type is stripselwidget.StripEnum.MidiTrack):
                    self.strips_list_selbank[i].set_rec(self.strips_list_widgets[id].get_rec())
                self.strips_list_selbank[i].set_sensitive(True)
            else:
                # ssid not present
                self.strips_list_selbank[i].set_ssid_name(None, "")
                self.strips_list_selbank[i].set_sensitive(False)
                self.strips_list_selbank[i].set_strip_type(stripselwidget.StripEnum.Empty)
                self.strips_list_selbank[i].set_select(False)
                self.strips_list_selbank[i].set_solo(False)
                self.strips_list_selbank[i].set_mute(False)
                self.strips_list_selbank[i].set_rec(False)
                self.avrCOM.moveFader(i, 0)

        for i in range(0, len(self.strips_list_widgets)):
            self.strips_list_widgets[i].set_bank_selected(self.strips_list_widgets[i].get_bank() == self.current_selected_bank)

    # Callback of current bank controls
    def bank_sel_clicked(self, widget, ichannel, bvalue, data=None):
        liblo.send(self.target, "/strip/select", ichannel, int(bvalue))

    def bank_rec_clicked(self, widget, ichannel, bvalue, data=None):
        liblo.send(self.target, "/strip/recenable", ichannel, int(bvalue))

    def bank_mute_clicked(self, widget, ichannel, bvalue, data=None):
        liblo.send(self.target, "/strip/mute", ichannel, int(bvalue))

    def bank_solo_clicked(self, widget, ichannel, bvalue, data=None):
        liblo.send(self.target, "/strip/solo", ichannel, int(bvalue))

    # Callbacks from OSC incoming messages
    def fader_osc_changed(self, widget, ichannel, fvalue, data=None):
        for i in range(0, len(self.strips_list_selbank)): #For each of the 8 faders
            if ichannel == self.strips_list_selbank[i].get_ssid():
                self.avrCOM.moveFader(i, fvalue)
                #print("fader received on channel '%d' with value '%f'" % (ichannel, fvalue))
                break

    def solo_osc_changed(self, widget, ichannel, bvalue, data=None):
        # print "solo received on channel '%d' with state '%s'" % (ichannel, bvalue)
        if ichannel in self.strips_ssid_id_dict:
            self.strips_list_widgets[self.strips_ssid_id_dict[ichannel]].set_solo(bvalue)
            if self.current_selected_bank is self.strips_list_widgets[self.strips_ssid_id_dict[ichannel]].get_bank():
                self.strips_list_selbank[(ichannel - 1) % 8].set_solo(bvalue)

    def mute_osc_changed(self, widget, ichannel, bvalue, data=None):
        # print "mute received on channel '%d' with state '%s'" % (ichannel, bvalue)
        if ichannel in self.strips_ssid_id_dict:
            self.strips_list_widgets[self.strips_ssid_id_dict[ichannel]].set_mute(bvalue)
            if self.current_selected_bank is self.strips_list_widgets[self.strips_ssid_id_dict[ichannel]].get_bank():
                self.strips_list_selbank[(ichannel - 1) % 8].set_mute(bvalue)

    def rec_osc_changed(self, widget, ichannel, bvalue, data=None):
        # print "rec received on channel '%d' with state '%s'" % (ichannel, bvalue)
        if ichannel in self.strips_ssid_id_dict:
            self.strips_list_widgets[self.strips_ssid_id_dict[ichannel]].set_rec(bvalue)
            if self.current_selected_bank is self.strips_list_widgets[self.strips_ssid_id_dict[ichannel]].get_bank():
                self.strips_list_selbank[(ichannel - 1) % 8].set_rec(bvalue)

    def select_osc_changed(self, widget, ichannel, bvalue, data=None):
        # print "select received on channel '%d' with state '%s'" % (ichannel, bvalue)
        if ichannel in self.strips_ssid_id_dict:
            new_selected_widget = self.strips_ssid_id_dict[ichannel]
            self.strips_list_widgets[new_selected_widget].set_selected(bvalue)

            # Check if bank has changed
            if bvalue: #Do not refresh the bank if selection is false!
                self.current_selected_bank = self.strips_list_widgets[new_selected_widget].get_bank()
                self.refresh_bank_sel()
    def meter_osc_changed(self, widget, ichannel, fvalue, data=None):
        #print ("meter on channel '%d' = '%s'" % (ichannel, fvalue))
        if ichannel in self.strips_ssid_id_dict:
            curr_widget = self.strips_ssid_id_dict[ichannel]
            self.strips_list_widgets[curr_widget].set_meter(fvalue)

    def smpte_osc_changed(self, widget, svalue, data=None):
        #print("SMPTE '%s'" % (svalue))
        self.btn_playpause.set_image(self.btn_playpause_GreenIcon)
        if self.bLooping:
            self.btn_loop.set_image(self.btn_loop_GreenIcon)
        GLib.source_remove(self.smpte_timer_ID) #Destroy previous timmer if running
        self.smpte_timer_ID = GLib.timeout_add(200, self.smpte_timeout) #Reset timmer

    def smpte_timeout(self):
        self.btn_playpause.set_image(self.btn_playpause_WhiteIcon)
        self.btn_loop.set_image(self.btn_loop_WhiteIcon)
        return True

    def list_osc_reply_track(self, widget, ssid, name, type, mute, solo, rec, inputs, outputs, data=None):
        self.strips_ssid_id_dict[ssid] = len(self.strips_list_widgets)
        self.strips_list_widgets.append(stripselwidget.StripSelWidget(len(self.strips_list_widgets),
                                                                      ssid,
                                                                      len(self.strips_list_widgets) // 8,
                                                                      name,
                                                                      type,
                                                                      mute,
                                                                      solo,
                                                                      inputs,
                                                                      outputs,
                                                                      rec))

    def list_osc_reply_bus(self, widget, ssid, name, type, mute, solo, inputs, outputs, data=None):
        self.strips_ssid_id_dict[ssid] = len(self.strips_list_widgets)
        self.strips_list_widgets.append(stripselwidget.StripSelWidget(len(self.strips_list_widgets),
                                                                      ssid,
                                                                      len(self.strips_list_widgets) // 8,
                                                                      name,
                                                                      type,
                                                                      mute,
                                                                      solo,
                                                                      inputs,
                                                                      outputs))

    def list_osc_reply_end(self, widget, data=None):
        self.fill_strips_table()

    def fill_strips_table(self):
        self.viewport_table.remove(self.table)
        self.number_of_banks = int(math.ceil(len(self.strips_list_widgets) / 8.0))
        self.table = Gtk.Grid()
        self.table.set_column_homogeneous(True)
        self.viewport_table.add(self.table)

        for i in range(0, len(self.strips_list_widgets)):
            self.table.attach(self.strips_list_widgets[i],
                              i - 8 * self.strips_list_widgets[i].get_bank(),
                              self.strips_list_widgets[i].get_bank(),
                              1,
                              1)
            self.strips_list_widgets[i].connect("strip_selected", self.strip_selected)

        if len(self.strips_list_widgets) < 8:
            #Insert empty columns to fill at least 8 columns, use and empty label to achive that
            for i in range( len(self.strips_list_widgets), 8):
                self.table.attach(Gtk.Label(),i,0,1,1)

        self.table.show_all()
        self.table.show()
        liblo.send(self.target, "/strip/select", self.strips_list_widgets[0].get_ssid(), 1) #Start by selcting the first srip
        self.select_osc_changed( None, self.strips_list_widgets[0].get_ssid(), True, None) #Force bank selection because if Ardour has already selected the first ssid the OSC feedback will not be send
        self.table_bank.set_sensitive(True)

    def on_meter_refresh_timeout(self):
        for stripCtl in self.strips_list_widgets:
            stripCtl.refresh_meter()
        GLib.timeout_add(self.timeout_meter_interval, self.on_meter_refresh_timeout)

    # Debug method to insert a line of ##### in terminal
    def dbg_insert_marker_line(self, widget, data=None):
        print("##################################################")

    def __init__(self):
        Gtk.Window.__init__(self, title="OSC Controller")
        # Reding config data from config.xml
        tree = ET.parse('config.xml')
        root = tree.getroot()

        osc_net = root.find('osc_net')
        daw_IP = osc_net.find('daw_ip').text
        daw_port = int(osc_net.find('daw_port').text)
        recv_port = int(osc_net.find('recv_port').text)

        avr_com = root.find('avr_com')
        serial_port = avr_com.find('serial_port').text
        baudrate = int(avr_com.find('baudrate').text)
        FADER_MIN = int(avr_com.find('fader_min').text)
        FADER_MAX = int(avr_com.find('fader_max').text)

        misc = root.find('misc')
        window_width = int(misc.find('window_width').text)
        window_height = int(misc.find('window_height').text)
        self.PIXELS_X_SECOND = int(misc.find('meter_waveform_speed').text)

        try:
            self.oscserver = oscserver.OSCServer(recv_port)
        except liblo.ServerError as err:
            print(str(err))
            sys.exit()

        try:
            self.target = liblo.Address(daw_IP, daw_port)
        except liblo.AddressError as err:
            print(str(err))
            sys.exit()

        self.vbox_top = Gtk.VBox()

        #Build the header bar
        self.btn_test = Gtk.Button.new_with_label("Test!") #TODO, debug button 2 remove
        self.btn_insert_marker_at_terminal = Gtk.Button.new_with_label("Dbg: insert ###") #TODO, debug button 2 remove

        self.btn_refresh = Gtk.Button()
        self.btn_refresh_icon = Gtk.Image. new_from_file("icons/reload_32.png")
        self.btn_refresh.set_image(self.btn_refresh_icon)

        self.btn_loop = Gtk.Button()
        self.btn_loop_WhiteIcon = Gtk.Image.new_from_file("icons/loopWhite.png")
        self.btn_loop_GreenIcon = Gtk.Image.new_from_file("icons/loopGreen.png")
        self.btn_loop.set_image(self.btn_loop_WhiteIcon)

        self.btn_playpause = Gtk.Button()
        self.btn_playpause_WhiteIcon = Gtk.Image.new_from_file("icons/play_pauseWhite.png")
        self.btn_playpause_GreenIcon = Gtk.Image.new_from_file("icons/play_pauseGreen.png")
        self.btn_playpause.set_image(self.btn_playpause_WhiteIcon)
        #5fa358ff aket es el color en estat d play

        self.headerBar = Gtk.HeaderBar()
        self.headerBar.set_title("SAPTouch")
        self.headerBar.set_subtitle("Ardour control surface")
        self.headerBar.set_show_close_button(True)
        self.set_titlebar(self.headerBar)
        self.headerBar.pack_start(self.btn_refresh)
        self.headerBar.pack_start(self.btn_test)
        self.headerBar.pack_start(self.btn_insert_marker_at_terminal)
        self.headerBar.pack_end(self.btn_loop)
        self.headerBar.pack_end(self.btn_playpause)

        #Global bool to store loop state
        self.bLooping = False

        # Build the central part of the gui, all strips list
        self.strips_list_widgets = []
        self.strips_ssid_id_dict = dict()
        self.number_of_banks = 0
        self.current_selected_strip_widget = None
        self.current_selected_bank = None

        self.scroll_tbl =Gtk.ScrolledWindow()
        self.table = Gtk.Label(label="Strip list is empty, click the refresh button to start DAW comunication")
        self.viewport_table = Gtk.Viewport()
        self.viewport_table.add(self.table)
        self.scroll_tbl.add(self.viewport_table)
        self.vbox_top.pack_start(self.scroll_tbl, expand=True, fill=True, padding=0)
        self.scroll_tbl.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Build the bottom part of the gui, bank settings
        self.table_bank = Gtk.Grid()
        self.table_bank.set_column_homogeneous(True)
        self.strips_list_selbank = []
        self.add(self.vbox_top)

        for i in range(0, 8):
            self.strips_list_selbank.append(stripctlwidget.StripCtlWidget())
            self.table_bank.attach(self.strips_list_selbank[i],i, 0, 1, 1)
            self.strips_list_selbank[i].connect("strip_selected", self.bank_sel_clicked, None)
            self.strips_list_selbank[i].connect("solo_changed", self.bank_solo_clicked, None)
            self.strips_list_selbank[i].connect("mute_changed", self.bank_mute_clicked, None)
            self.strips_list_selbank[i].connect("rec_changed", self.bank_rec_clicked, None)
        self.table_bank.set_sensitive(False)
        self.vbox_top.pack_end(self.table_bank, expand=False, fill=False, padding=0)

        #Adding the AVR serial control object
        self.avrCOM = pyFaderSerialCOM.FaderCOM(serial_port, baudrate, FADER_MIN, FADER_MAX)
        self.avrCOM.connect("fader_changed", self.fader_moved)
        self.avrCOM.connect("fader_untouched", self.fader_untouched)

        self.set_resizable(False)
        self.set_default_size(window_width, window_height)
        self.show_all()

        #Refine intial bank widgets state
        for i in range(0, 8):
            self.strips_list_selbank[i].set_strip_type(stripselwidget.StripEnum.Empty)
        self.show()

        self.btn_test.connect("clicked", self.btn_test_clicked, None) #TODO DBG button to rmeove
        self.btn_insert_marker_at_terminal.connect("clicked", self.dbg_insert_marker_line, None)  #TODO DBG button to rmeove
        self.btn_refresh.connect("clicked", self.refresh_strip_list, None)
        self.btn_playpause.connect("clicked", self.btn_playStop_clicked, None)
        self.btn_loop.connect("clicked", self.btn_loop_clicked, None)

        self.connect("destroy", self.destroy)
        self.connect("delete_event", self.delete_event)

        # Connect OSC message received signals
        self.oscserver.OSCSignals.connect("list_reply_track", self.list_osc_reply_track, None)
        self.oscserver.OSCSignals.connect("list_reply_bus", self.list_osc_reply_bus, None)
        self.oscserver.OSCSignals.connect("list_reply_end", self.list_osc_reply_end, None)
        self.oscserver.OSCSignals.connect("fader_changed", self.fader_osc_changed, None)
        self.oscserver.OSCSignals.connect("solo_changed", self.solo_osc_changed, None)
        self.oscserver.OSCSignals.connect("mute_changed", self.mute_osc_changed, None)
        self.oscserver.OSCSignals.connect("rec_changed", self.rec_osc_changed, None)
        self.oscserver.OSCSignals.connect("select_changed", self.select_osc_changed, None)
        self.oscserver.OSCSignals.connect("meter_changed", self.meter_osc_changed, None)
        self.oscserver.OSCSignals.connect("smpte_changed", self.smpte_osc_changed, None)
        self.smpte_timer_ID = GLib.timeout_add(100, self.smpte_timeout) #Create a timer

        #Meters, global refress timer
        self.timeout_meter_interval = round( 1000.0 / self.PIXELS_X_SECOND )#Timeout interval in milliseconds
        GLib.timeout_add(self.timeout_meter_interval, self.on_meter_refresh_timeout)

        #Set theme
        screen = Gdk.Screen.get_default()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("saptouch_theme.css")

        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def main(self):
        self.oscserver.start()
        Gtk.main()


print(__name__)
if __name__ == "__main__":
    base = ControllerGUI()
    base.main()


#TODO accions interssants a afegir al OSC
#/access_action/Common/toggle-editor-and-mixer #conumta entre mesclador/editor moooola
#/access_action/Editor/set-playhead #mou el playhead al mouse!
#/access_action/Editor/snap-off
#/access_action/Editor/snap-normal
#/access_action/Editor/snap-magnetic
# /undo #Ctrl-Z yes!
# /redo #Ctrl-Z yes!
# /save_state es equivalent a control+s o session>>save
# /jog i /jog_mode 0 per control del jog-wheel, ajuda a moure el curspr amb un encoder
# /access_action/Region/toggle-region-lock # lock and unlocks currently selected region
# /access_action/Editor/split-region #Split the selected region, identic a S

#TODO crear un tema amb css per sobrescriure el tema d escriptori, miret el stripctlwidget per veure com apliques css al boto edit
