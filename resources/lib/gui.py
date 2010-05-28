# -*- coding: utf-8 -*-

import os
import sys
import base64
import xbmc
import xbmcgui
import transmissionrpc
from basictypes.bytes import Bytes
from repeater import Repeater

_ = sys.modules[ "__main__" ].__language__
__settings__ = xbmc.Settings(path=os.getcwd())

KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

class TransmissionGUI(xbmcgui.WindowXMLDialog):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, bforeFallback=0):
        params = {
            'address': __settings__.getSetting('rpc_host'),
            'port': __settings__.getSetting('rpc_port'),
            'user': __settings__.getSetting('rpc_user'),
            'password': __settings__.getSetting('rpc_password')
        }
        self.transmission = transmissionrpc.transmission.Client(**params)
        self.list = {}
        self.torrents = {}
    def onInit(self):
        self.updateTorrents()
        self.repeater = Repeater(1.0, self.updateTorrents)
        self.repeater.start()
    def shutDown(self):
        print "terminating repeater"
        self.repeater.stop()
        print "closing transmission gui"
        self.close()
    def updateTorrents(self):
        list = self.getControl(20)
        torrents = self.transmission.info()
        for i, torrent in torrents.iteritems():
            statusline = "[%(status)s] %(down)s down (%(pct).2f%%), %(up)s up (Ratio: %(ratio).2f)" % \
                {'down': Bytes.format(torrent.downloadedEver), 'pct': torrent.progress, \
                'up': Bytes.format(torrent.uploadedEver), 'ratio': torrent.ratio, \
                'status': torrent.status}
            if torrent.status is 'downloading':
                statusline += " ETA: %(eta)s" % \
                    {'eta': torrent.eta}
            if i not in self.list:
                # Create a new list item
                l = xbmcgui.ListItem(label=torrent.name, label2=statusline)
                list.addItem(l)
                self.list[i] = l
            else:
                # Update existing list item
                l = self.list[i]
            self.torrents = torrents
            l.setLabel(torrent.name)
            l.setLabel2(statusline)
            l.setProperty('TorrentID', str(i))
            l.setProperty('TorrentProgress', "%.2ff" % torrent.progress)
            l.setInfo('torrent', torrent.fields)
            l.setInfo('video', {'episode': int(torrent.progress)})

        removed = [id for id in self.list.keys() if id not in torrents.keys()]
        if len(removed) > 0:
            # Clear torrents from the list that have been removed
            for id in removed:
                del self.list[id]
            list.reset()
            for id, item in self.list.iteritems():
                list.addItem(item)
    def onAction(self, action):
        buttonCode =  action.getButtonCode()
        actionID   =  action.getId()
        if (buttonCode == KEY_BUTTON_BACK or buttonCode == KEY_KEYBOARD_ESC):
            self.shutDown()
    def onClick(self, controlID):
        list = self.getControl(20)
        if (controlID == 11):
            # Add torrent
            d = xbmcgui.Dialog()
            f = d.browse(1, _(0), 'files', '.torrent')
            self.transmission.add_url(f)
        if (controlID == 12):
            # Remove selected torrent
            item = list.getSelectedItem()
            if item and xbmcgui.Dialog().yesno(_(0), 'Remove \'%s\'?' % self.torrents[int(item.getProperty('TorrentID'))].name):
                remove_data = xbmcgui.Dialog().yesno(_(0), 'Remove data as well?')
                self.transmission.remove(int(item.getProperty('TorrentID')), remove_data)
        if (controlID == 13):
            # Stop selected torrent
            item = list.getSelectedItem()
            if item:
                self.transmission.stop(int(item.getProperty('TorrentID')))
        if (controlID == 14):
            # Start selected torrent
            item = list.getSelectedItem()
            if item:
                t = int(item.getProperty('TorrentID'))
                self.transmission.start(int(item.getProperty('TorrentID')))
        if (controlID == 15):
            # Stop all torrents
            self.transmission.stop(self.torrents.keys())
        if (controlID == 16):
            # Start all torrents
            self.transmission.start(self.torrents.keys())
        if (controlID == 17):
            # Exit button
            self.shutDown()
        if (controlID == 20):
            return
            # A torrent was chosen, show details
            item = list.getSelectedItem()
            w = TorrentInfoGUI("script-Transmission-main.xml",os.getcwd() ,"default")
            w.setTorrent(int(item.getProperty('TorrentID')))
            w.doModal()
            del w
    def onFocus(self, controlID):
        pass

class TorrentInfoGUI(xbmcgui.WindowXMLDialog):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, bforeFallback=0):
        self.torrent_id = None
        pass
    def setTorrent(t_id):
        self.torrent_id = t_id
    def onInit(self):
        pass
    def onAction(self, action):
        buttonCode =  action.getButtonCode()
        actionID   =  action.getId()
        if (buttonCode == KEY_BUTTON_BACK or buttonCode == KEY_KEYBOARD_ESC):
            self.close()
    def onClick(self, controlID):
        pass
    def onFocus(self, controlID):
        pass