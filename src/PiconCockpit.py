#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2021 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	For more information on the GNU General Public License see:
#	<http://www.gnu.org/licenses/>.


from Debug import logger
import os
import uuid
from __init__ import _
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.Pixmap import Pixmap
from Components.Button import Button
from Components.Sources.List import List
from Components.ActionMap import HelpableActionMap
from Components.config import config
from FileUtils import readFile
from ConfigScreen import ConfigScreen
from PiconDownloadProgress import PiconDownloadProgress
from ConfigInit import ConfigInit
from twisted.web.client import downloadPage
from Screens.MessageBox import MessageBox


picon_info_file = "picon_info.txt"
picon_list_file = "zz_picon_list.txt"


class PiconCockpit(Screen, HelpableScreen, ConfigInit):

	def __init__(self, session):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.skinName = ["PiconCockpit"]
		ConfigInit.__init__(self, [], [], [], [])

		self["actions"] = HelpableActionMap(
			self,
			"PICActions",
			{
				"MENU":		(self.menu,	_("Menu")),
				"EXIT":		(self.exit,	_("Exit")),
				"RED":		(self.exit,	_("Exit")),
				"GREEN":	(self.green,	_("Download")),
			},
			prio=-1
		)

		self.last_picon_set = config.plugins.piconcockpit.last_picon_set.value
		self.picon_dir = config.usage.configselection_piconspath.value
		self.setTitle(_("PiconCockpit"))
		self["list"] = List()
		self["picon"] = Pixmap()
		self["key_green"] = Button(_("Download"))
		self["key_red"] = Button(_("Exit"))
		self["key_yellow"] = Button()
		self["key_blue"] = Button()
		self['list'].onSelectionChanged.append(self.downloadPreview)
		self.onShow.append(self.onDialogShow)
		logger.debug("picon_dir: %s", self.picon_dir)
		self.getPiconSetInfo()

	def onDialogShow(self):
		logger.info("...")
		self.fillList()

	def getPiconSetInfo(self):
		if os.path.exists(self.picon_dir):
			url = os.path.join(config.plugins.piconcockpit.picon_server.value, "picons", picon_info_file)
			download_file = os.path.join(self.picon_dir, picon_info_file)
			logger.debug("url: %s, download_file: %s", url, download_file)
			downloadPage(url, download_file).addCallback(self.fillList).addErrback(self.downloadError, url)
		else:
			self.session.open(MessageBox, _("Picon path directory does not exist" + ": " + self.picon_dir), MessageBox.TYPE_ERROR)

	def downloadError(self, _result, _url):
		logger.error("url: %s, result: %s", _url, _result)
		self.session.open(MessageBox, _("Picon server access failed"), MessageBox.TYPE_ERROR)

	def menu(self):
		picon_set = self["list"].getCurrent()
		if picon_set:
			self.last_picon_set = picon_set[4]
		self.session.open(ConfigScreen)

	def exit(self):
		logger.debug("...")
		picon_set = self["list"].getCurrent()
		if picon_set:
			logger.debug("last_picon_set: %s", picon_set[4])
			config.plugins.piconcockpit.last_picon_set.value = picon_set[4]
			config.plugins.piconcockpit.last_picon_set.save()
			os.popen("rm /tmp/*.png")
		self.close()

	def green(self):
		picon_set = self["list"].getCurrent()
		logger.debug("picon_set: %s", str(picon_set))
		if picon_set:
			url = os.path.join(picon_set[1], picon_list_file)
			download_file = os.path.join(self.picon_dir, picon_list_file)
			logger.debug("url: %s, download_file: %s", url, download_file)
			downloadPage(url, download_file).addCallback(self.downloadPicons, picon_set).addErrback(self.downloadError)

	def listBouquets(self, adir):
		alist = []
		try:
			for afile in os.listdir(adir):
				path = os.path.join(adir, afile)
				if afile.startswith("userbouquet.") and afile.endswith(".tv") and "LastScanned" not in afile:
					alist.append(path)
		except OSError as e:
			logger.error("failed: e: %s", e)
		return alist

	def getUserBouquetPicons(self):
		picons = []
		bouquets = self.listBouquets("/etc/enigma2")
		for bouquet in bouquets:
			lines = readFile(bouquet).splitlines()
			for line in lines:
				if not line.startswith("#NAME"):
					ref = line.split(" ")[1]
					ref = ref.replace(":", "_")
					ref = ref[:len(ref) - 1]
					picon = ref + ".png"
					picons.append(picon)
		return picons

	def downloadPicons(self, _result=None, picon_set=None):
		if config.plugins.piconcockpit.all_picons.value:
			picons = readFile(os.path.join(self.picon_dir, picon_list_file)).splitlines()
		else:
			picons = self.getUserBouquetPicons()
		logger.debug("picons: %s", picons)
		if picons:
			if config.plugins.piconcockpit.delete_before_download:
				os.system("rm " + os.path.join(self.picon_dir, "*.png"))
			self.session.open(PiconDownloadProgress, picon_set[1], picons, self.picon_dir)

	def fillList(self, _result=None):
		logger.info("...")
		picon_set_list = readFile(os.path.join(self.picon_dir, picon_info_file)).splitlines()
		self.parseSettingsOptions(picon_set_list)
		picon_list = self.parsePiconSetList(picon_set_list)
		picon_list.sort(key=lambda x: x[0])
		self["list"].setList(picon_list)
		start_index = -1
		for i, picon_set in enumerate(picon_list):
			if picon_set[4] == self.last_picon_set:
				start_index = i
				break
		logger.debug("start_index: %s", start_index)
		if start_index >= 0:
			self["list"].setIndex(start_index)
		self.downloadPreview()

	def parseSettingsOptions(self, picon_set_list):
		logger.debug("...")
		size_list = {"all"}
		bit_list = {"all"}
		creator_list = {"all"}
		satellite_list = {"all"}
		for picon_set in picon_set_list:
			if not picon_set.startswith('<meta'):
				info_list = picon_set.split(';')
				if len(info_list) >= 9:
					satellite_list.add(info_list[4])
					creator_list.add(info_list[5])
					bit_list.add(info_list[6].replace(' ', '').lower().replace('bit', ' bit'))
					size_list.add(info_list[7].replace(' ', '').lower())
		ConfigInit.__init__(self, list(size_list), list(bit_list), list(creator_list), list(satellite_list))

	def parsePiconSetList(self, picon_set_list):
		logger.debug("last_picon_set: %s", config.plugins.piconcockpit.last_picon_set.value)
		picon_list = []
		for picon_set in picon_set_list:
			if not picon_set.startswith('<meta'):
				info_list = picon_set.split(';')
				if len(info_list) >= 9:
					dir_url = os.path.join(config.plugins.piconcockpit.picon_server.value, info_list[0])
					pic_url = os.path.join(config.plugins.piconcockpit.picon_server.value, info_list[0], info_list[1])
					date = info_list[2]
					name = info_list[3]
					satellite = info_list[4]
					creator = info_list[5]
					bit = (info_list[6].replace(' ', '').lower()).replace('bit', ' bit')
					size = info_list[7].replace(' ', '').lower()
					uploader = info_list[8]
					identifier = str(uuid.uuid4())
					signature = "%s | %s - %s | %s | %s | %s" % (satellite, creator, name, size, bit, uploader)
					name = signature + " | %s" % date
					if config.plugins.piconcockpit.satellite.value in ["all", satellite] and\
						config.plugins.piconcockpit.creator.value in ["all", creator] and\
						config.plugins.piconcockpit.size.value in ["all", size] and\
						config.plugins.piconcockpit.bit.value in ["all", bit]:
						picon_list.append((name, dir_url, pic_url, identifier, signature))
		return picon_list

	def downloadPreview(self):
		logger.debug("...")
		self["picon"].hide()
		if self['list'].getCurrent():
			logger.debug("current: %s", str(self["list"].getCurrent()))
			picon_name = self['list'].getCurrent()[2]
			logger.debug("picon_name: %s", picon_name)
			picon_path = os.path.join("/tmp", self['list'].getCurrent()[3] + ".png")
			if not os.path.exists(picon_path):
				downloadPage(picon_name, picon_path).addCallback(self.showPreview, picon_path).addErrback(self.downloadError)
			else:
				self.showPreview(None, picon_path)

	def showPreview(self, _result=None, path=None):
		logger.debug("path: %s", path)
		self["picon"].show()
		self["picon"].instance.setPixmapFromFile(path)
