#!/usr/bin/env python

import pygtk
import gobject
import gtk
import liblo
import sys
import oscserver
import stripselwidget
import stripctlwidget
import math
import xml.etree.ElementTree as ET
import ast


pygtk.require('2.0')
gobject.threads_init()  # You need to call that to avoid liblo server thread to interact with gui thread

""" ControllerGUI class
This class implements a gtk GUI for sending osc messages using the liblo.send() method.
The GUI is also able to receive OSC messages in a signal-handler model using OSCServer class.
"""


class ControllerGUI:
    def delete_event(self, widget, event, data=None):
        self.oscserver.stop()
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def btn_play_clicked(self, widget, data=None):
        liblo.send(self.target, "/transport_play")

    def btn_stop_clicked(self, widget, data=None):
        liblo.send(self.target, "/transport_stop")

         #def callback(range, scroll, value, arg1, arg2, user_param1, ...)

    def btn_quit_clicked(selfself, widget, data=None):
        quitDialog = gtk.MessageDialog(parent=None,
                            flags=0,
                            type=gtk.MESSAGE_QUESTION,
                            buttons=gtk.BUTTONS_YES_NO,
                            message_format=None)

        quitDialog.set_markup("Are you sure to quit?")
        resp = quitDialog.run()
        quitDialog.destroy()
        if resp == gtk.RESPONSE_YES:
            gtk.main_quit()

    def fader_changed(self, widget, scroll, value, arg1):
        if self.test_fader_touched:
            selSSID = self.strips_list_widgets[self.current_selected_strip_widget].get_ssid()
            #liblo.send(self.target, "/strip/fader", selSSID, self.test_fader.get_value())
            liblo.send(self.target, "/strip/fader", selSSID, value)
        return True

    def fader_touched(self, widget, event, arg1):
        selSSID = self.strips_list_widgets[self.current_selected_strip_widget].get_ssid()
        liblo.send(self.target, "/strip/fader/touch", float(selSSID), 1.0) #Using floats it works
        #liblo.send(self.target, "/strip/fader/touch", selSSID, 1)  # Using int it does not work
        self.test_fader_touched = True

    def fader_untouched(self, widget, event, arg1):
        selSSID = self.strips_list_widgets[self.current_selected_strip_widget].get_ssid()
        self.test_fader_touched = False
        liblo.send(self.target, "/strip/fader/touch", selSSID, 0)

    def strip_selected(self, widget, issid, ibank, data=None):
        liblo.send(self.target, "/strip/select", issid, 1)

    def refresh_strip_list(self, widget, data=None):
        self.strips_list_widgets = [] #Clear the list
        self.strips_ssid_id_dict = dict() #Clear the id ssid dictionary
        # Config the surface as infinite banks, track setting, strip feedback and fader as position values
        liblo.send(self.target, "/set_surface", 0.0, 7.0, 3.0, 1.0, 0.0) #Sending as floats works as ints... doesn
        liblo.send(self.target, "/strip/list")
 
    def refresh_bank_sel(self):
        for i in range(0, len(self.strips_list_selbank)):
            working_ssid = self.current_selected_bank * 8 + i + 1 # plus one because ardour indexes from 1
            if working_ssid in self.strips_ssid_id_dict:
                id = self.strips_ssid_id_dict[working_ssid]
                self.strips_list_selbank[i].set_ssid_name(working_ssid, self.strips_list_widgets[id].stripname)
                self.strips_list_selbank[i].set_strip_type( self.strips_list_widgets[id].type)
                self.strips_list_selbank[i].set_select(self.strips_list_widgets[id].get_selected())
                self.strips_list_selbank[i].set_solo(self.strips_list_widgets[id].solo)
                self.strips_list_selbank[i].set_mute(self.strips_list_widgets[id].mute)
                if (self.strips_list_widgets[id].type is stripselwidget.StripEnum.AudioTrack) or (self.strips_list_widgets[id].type is stripselwidget.StripEnum.MidiTrack):
                    self.strips_list_selbank[i].set_rec(self.strips_list_widgets[id].rec)
                self.strips_list_selbank[i].show()
            else:
                #ssid not present
                self.strips_list_selbank[i].hide()

    # Callback of current bank controls
    def bank_sel_clicked (self, widget, ichannel, bvalue, data=None):
        liblo.send(self.target, "/strip/select", ichannel, 1)

    def bank_rec_clicked(self, widget, ichannel, bvalue, data=None):
        liblo.send(self.target, "/strip/recenable", ichannel, int(bvalue))

    def bank_mute_clicked (self, widget, ichannel, bvalue, data=None):
        liblo.send(self.target, "/strip/mute", ichannel, int(bvalue))

    def bank_solo_clicked (self, widget, ichannel, bvalue, data=None):
        liblo.send(self.target, "/strip/solo", ichannel, int(bvalue))

    # Callbacks from OSC incoming messages
    def fader_osc_changed(self, widget, ichannel, fvalue, data=None):
        if self.current_selected_strip_widget is not None:
            if ichannel == self.strips_list_widgets[self.current_selected_strip_widget].get_ssid():
                self.test_fader.set_value(fvalue)
        #print "fader received on channel '%d' with value '%f'" % (ichannel, fvalue)

    def solo_osc_changed(self, widget, ichannel, bvalue, data=None):
        #print "solo received on channel '%d' with state '%s'" % (ichannel, bvalue)
        if ichannel in self.strips_ssid_id_dict:
            self.strips_list_widgets[self.strips_ssid_id_dict[ichannel]].set_solo(bvalue)
            if self.current_selected_bank is self.strips_list_widgets[self.strips_ssid_id_dict[ichannel]].get_bank():
                self.strips_list_selbank[(ichannel - 1) % 8].set_solo(bvalue)

    def mute_osc_changed(self, widget, ichannel, bvalue, data=None):
        #print "mute received on channel '%d' with state '%s'" % (ichannel, bvalue)
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
        if ichannel in self.strips_ssid_id_dict and bvalue:
            new_selected_widget = self.strips_ssid_id_dict[ichannel]
            self.strips_list_widgets[self.current_selected_strip_widget].set_selected(False)
            self.strips_list_widgets[new_selected_widget].set_selected(True)

            # Check if bank has changed
            if self.current_selected_bank != self.strips_list_widgets[new_selected_widget].get_bank():
                self.current_selected_bank = self.strips_list_widgets[new_selected_widget].get_bank()
                self.refresh_bank_sel()
            else:
                #Uselect current selected
                bank_id = (self.strips_list_widgets[self.current_selected_strip_widget].get_ssid() - 1) % 8
                self.strips_list_selbank[bank_id].set_select(False)

                #Select the new one
                bank_id = (ichannel - 1) % 8
                self.strips_list_selbank[bank_id].set_select(self.strips_list_widgets[new_selected_widget].get_selected())

            self.current_selected_strip_widget = new_selected_widget

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
        self.current_selected_strip_widget = 0 # TODO use the receivied OSC mesages to set the selected widget correctly as Ardour GUI
        self.viewport_table.remove(self.table)
        self.number_of_banks = int(math.ceil(len(self.strips_list_widgets) / 8.0))
        self.table = gtk.Table(rows=self.number_of_banks, columns=8, homogeneous=True)
        self.viewport_table.add(self.table)

        for i in range(0, len(self.strips_list_widgets)):
            self.table.attach(self.strips_list_widgets[i], left_attach=i - 8 * self.strips_list_widgets[i].get_bank(),
                              right_attach=i - 8 * self.strips_list_widgets[i].get_bank() + 1,
                              top_attach=self.strips_list_widgets[i].get_bank(),
                              bottom_attach=self.strips_list_widgets[i].get_bank() + 1,
                              xoptions=gtk.EXPAND | gtk.FILL, yoptions= gtk.EXPAND)
            self.strips_list_widgets[i].connect("strip_selected", self.strip_selected)
        self.table.show_all()
        self.table.show()

    # Debug method to insert a line of ##### in terminal
    def dbg_insert_marker_line(self, widget, data=None):
        print "##################################################"

    def __init__(self):

        # Reding config data from config.xml
        tree = ET.parse('config.xml')
        root = tree.getroot()
        osc_net = root.find('osc_net')
        daw_IP = osc_net.find('daw_ip').text
        daw_port = int(osc_net.find('daw_port').text)
        recv_port = int(osc_net.find('recv_port').text)
        misc = root.find('misc')
        fullscreenmode = ast.literal_eval(misc.find('fullscreen').text)

        try:
            self.oscserver = oscserver.OSCServer(recv_port)
        except liblo.ServerError, err:
            print str(err)
            sys.exit()

        try:
            self.target = liblo.Address(daw_IP, daw_port)
        except liblo.AddressError, err:
            print str(err)
            sys.exit()

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.vbox_top = gtk.VBox()

        # Build the top part of the gui, general buttons
        self.hbox_top = gtk.HBox()
        self.btn_refresh = gtk.Button("Refresh")
        self.btn_insert_marker_at_terminal = gtk.Button("Dbg: insert ###")
        self.btn_quit = gtk.Button("Quit")
        self.hbox_top.pack_start(self.btn_refresh, expand=False, fill=False)
        self.hbox_top.pack_start(self.btn_insert_marker_at_terminal, expand=False, fill=False)
        self.hbox_top.pack_end(self.btn_quit, expand=False, fill=False)
        self.vbox_top.pack_start(self.hbox_top, expand=False, fill=False)


        # Build the central part of the gui, all strips list
        self.strips_list_widgets = []
        self.strips_ssid_id_dict = dict()
        self.number_of_banks = 0
        self.current_selected_strip_widget = None
        self.current_selected_bank = None

        self.scroll_tbl = gtk.ScrolledWindow()
        self.table = gtk.Label("strip list is empty")
        self.viewport_table = gtk.Viewport()
        self.viewport_table.add(self.table)
        self.scroll_tbl.add(self.viewport_table)
        self.vbox_top.pack_start(self.scroll_tbl)
        self.scroll_tbl.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        # Build the bottom part of the gui, bank settings
        self.table_bank = gtk.Table(rows=1, columns=8, homogeneous=True)
        self.strips_list_selbank = []
        # TODO start with a hide state and then enable it
        for i in range(0, 8):
            self.strips_list_selbank.append(stripctlwidget.StripCtlWidget())
            self.table_bank.attach(self.strips_list_selbank[i], left_attach=i,
                              right_attach=i + 1,
                              top_attach=0,
                              bottom_attach=1,
                              xoptions=gtk.EXPAND | gtk.FILL, yoptions=gtk.EXPAND)
            self.strips_list_selbank[i].connect("strip_selected", self.bank_sel_clicked, None)
            self.strips_list_selbank[i].connect("solo_changed", self.bank_solo_clicked, None)
            self.strips_list_selbank[i].connect("mute_changed", self.bank_mute_clicked, None)
            self.strips_list_selbank[i].connect("rec_changed", self.bank_rec_clicked, None)
        self.vbox_top.pack_start(self.table_bank)

        # Add a horizontal slider to the bottom for testing without faders
        self.test_fader = gtk.HScale()
        self.test_fader.set_range(0.0, 1.0)
        self.test_fader.set_value(0.0)
        self.vbox_top.pack_start(self.test_fader)
        self.test_fader.add_events(gtk.gdk.BUTTON_PRESS_MASK )
        self.test_fader.connect("change-value", self.fader_changed, None)
        self.test_fader.connect("button-press-event", self.fader_touched, None)
        self.test_fader.connect("button-release-event", self.fader_untouched, None)

        self.window.add(self.vbox_top)
        self.window.set_size_request(1280, 800)
        self.window.show_all()
        if fullscreenmode:
            self.window.fullscreen()
        self.window.show()

        # self.btn_play.connect("clicked", self.btn_play_clicked, None)
        # self.btn_stop.connect("clicked", self.btn_stop_clicked, None)
        self.btn_quit.connect("clicked", self.btn_quit_clicked, None)

        self.btn_refresh.connect("clicked", self.refresh_strip_list, None)
        self.btn_insert_marker_at_terminal.connect("clicked", self.dbg_insert_marker_line, None)

        self.window.connect("destroy", self.destroy)
        self.window.connect("delete_event", self.delete_event)

        # Connect OSC message received signals
        self.oscserver.OSCSignals.connect("list_reply_track", self.list_osc_reply_track, None)
        self.oscserver.OSCSignals.connect("list_reply_bus", self.list_osc_reply_bus, None)
        self.oscserver.OSCSignals.connect("list_reply_end", self.list_osc_reply_end, None)
        self.oscserver.OSCSignals.connect("fader_changed", self.fader_osc_changed, None)
        self.oscserver.OSCSignals.connect("solo_changed", self.solo_osc_changed, None)
        self.oscserver.OSCSignals.connect("mute_changed", self.mute_osc_changed, None)
        self.oscserver.OSCSignals.connect("rec_changed", self.rec_osc_changed, None)
        self.oscserver.OSCSignals.connect("select_changed", self.select_osc_changed, None)

        self.test_fader_touched = False

    def main(self):
        self.oscserver.start()
        gtk.main()


print __name__
if __name__ == "__main__":
    base = ControllerGUI()
    base.main()
