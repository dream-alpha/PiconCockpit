#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2025 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


import os
import uuid
from twisted.web.client import downloadPage
from APIs.ServiceData import getServiceList, getTVBouquets, getRadioBouquets
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Pixmap import Pixmap
from Components.Button import Button
from Components.ActionMap import ActionMap
from Components.config import config, configfile
from Tools.LoadPixmap import LoadPixmap
from .Debug import logger
from .__init__ import _
from .FileUtils import readFile, createDirectory
from .ConfigScreen import ConfigScreen
from .PiconDownloadProgress import PiconDownloadProgress
from .ConfigInit import ConfigInit
from .SkinUtils import getSkinName
from .CockpitContextMenu import CockpitContextMenu
from .List import List


picon_info_file = "picon_info.txt"
picon_list_file = "zz_picon_list.txt"


class PiconCockpit(Screen):
    def __init__(self, session):
        logger.info("...")
        Screen.__init__(self, session)
        self.skinName = getSkinName("PiconCockpit")

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "MenuActions"],
            {
                "menu":		self.openContextMenu,
                "cancel":	self.exit,
                "red":		self.exit,
                "green":	self.green,
            },
            prio=-1
        )

        self.last_picon_set = config.plugins.piconcockpit.last_picon_set.value
        self.setTitle(_("PiconCockpit"))
        self["list"] = List()
        self["preview"] = Pixmap()
        self["key_green"] = Button(_("Download"))
        self["key_red"] = Button(_("Exit"))
        self["key_yellow"] = Button()
        self["key_blue"] = Button()
        self.first_start = True
        self.onLayoutFinish.append(self.__onLayoutFinish)

    def onSelectionChanged(self):
        logger.info("...")
        self.downloadPreview()

    def __onLayoutFinish(self):
        logger.info("...")
        self.picon_dir = config.usage.configselection_piconspath.value
        if not os.path.exists(self.picon_dir):
            createDirectory(self.picon_dir)
        if self.first_start:
            self.first_start = False
            self.getPiconSetInfo()
        else:
            self.createList(False)

    def getPiconSetInfo(self):
        logger.info("...")
        url = os.path.join(
            config.plugins.piconcockpit.picon_server.value, "picons", picon_info_file)
        download_file = os.path.join(
            self.picon_dir, picon_info_file).replace(" ", "%20")
        logger.debug("url: %s, download_file: %s", url, download_file)
        downloadPage(url, download_file).addCallback(
            self.gotPiconSetInfo).addErrback(self.downloadError, url)

    def gotPiconSetInfo(self, result):
        logger.info("result: %s", result)
        self.createList(True)
        self.onSelectionChanged()

    def downloadError(self, result, url):
        logger.info("...")
        logger.error("url: %s, result: %s", url, result)
        self.session.open(MessageBox, _(
            "Picon server access failed"), MessageBox.TYPE_ERROR)
        self.createList(False)

    def openContextMenu(self):
        self.session.open(
            CockpitContextMenu,
            self,
        )

    def openConfigScreen(self):
        logger.info("...")
        picon_set = self["list"].getCurrent()
        if picon_set:
            self.last_picon_set = picon_set[4]
        self.session.openWithCallback(
            self.openConfigScreenCallback, ConfigScreen, config.plugins.piconcockpit)

    def openConfigScreenCallback(self, _result=None):
        logger.info("...")
        self.first_start = True
        self.__onLayoutFinish()

    def exit(self):
        logger.info("...")
        self['list'].onSelectionChanged = []
        picon_set = self["list"].getCurrent()
        if picon_set:
            logger.debug("last_picon_set: %s", picon_set[4])
            config.plugins.piconcockpit.last_picon_set.value = picon_set[4]
            config.plugins.piconcockpit.last_picon_set.save()
            configfile.save()
            os.popen("rm /tmp/*.png")
        self.close()

    def green(self):
        picon_set = self["list"].getCurrent()
        logger.debug("picon_set: %s", str(picon_set))
        if picon_set:
            url = os.path.join(
                picon_set[1], picon_list_file).replace(" ", "%20")
            download_file = os.path.join(self.picon_dir, picon_list_file)
            logger.debug("url: %s, download_file: %s", url, download_file)
            downloadPage(url, download_file).addCallback(
                self.downloadPicons, picon_set).addErrback(self.downloadError, url)

    def listBouquetServices(self):
        logger.info("...")
        bouquets = getTVBouquets()
        bouquets += getRadioBouquets()
        logger.debug("bouquets: %s", bouquets)
        services = []
        for bouquet in bouquets:
            if "Last Scanned" not in bouquet[1]:
                services += getServiceList(bouquet[0])
        logger.debug("services: %s", services)
        return services

    def getUserBouquetPicons(self):
        logger.info("...")
        picons = []
        services = self.listBouquetServices()
        for service in services:
            logger.debug("service: %s", service)
            ref = service[0]
            ref = ref.replace(":", "_")
            ref = ref[:len(ref) - 1]
            picon = ref + ".png"
            logger.debug("picon: %s", picon)
            if picon.startswith("1_"):
                picons.append(picon)
            else:
                logger.debug("skipping picon: %s", picon)
        return picons

    def downloadPicons(self, _result=None, picon_set=None):
        logger.info("...")
        if config.plugins.piconcockpit.all_picons.value:
            picons = readFile(os.path.join(
                self.picon_dir, picon_list_file)).splitlines()
        else:
            picons = self.getUserBouquetPicons()
        logger.debug("picons: %s", picons)
        if picons:
            if config.plugins.piconcockpit.delete_before_download:
                os.popen("rm " + os.path.join(self.picon_dir, "*.png"))
            self.session.open(PiconDownloadProgress,
                              picon_set[1], picons, self.picon_dir)

    def createList(self, fill):
        logger.info("fill: %s", fill)
        self['list'].onSelectionChanged = []
        picon_list = []
        self["preview"].hide()
        start_index = -1
        if fill:
            picon_set_list = readFile(os.path.join(
                self.picon_dir, picon_info_file)).splitlines()
            self.parseSettingsOptions(picon_set_list)
            picon_list = self.parsePiconSetList(picon_set_list)
            picon_list.sort(key=lambda x: x[0])
            for i, picon_set in enumerate(picon_list):
                picon_set = picon_set[0]
                if picon_set[4] == self.last_picon_set:
                    logger.debug("picon_set: %s, last_picon_set: %s",
                                 picon_set[4], self.last_picon_set)
                    start_index = i
                    break
        self["list"].setList(picon_list)
        self['list'].onSelectionChanged.append(self.onSelectionChanged)
        logger.debug("start_index: %s", start_index)
        if start_index >= 0:
            self["list"].moveToIndex(start_index)

    def parseSettingsOptions(self, picon_set_list):
        logger.info("...")
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
                    bit_list.add(info_list[6].replace(
                        ' ', '').lower().replace('bit', ' bit'))
                    size_list.add(info_list[7].replace(' ', '').lower())
        if picon_set_list:
            ConfigInit(list(size_list), list(bit_list),
                       list(creator_list), list(satellite_list))

    def parsePiconSetList(self, picon_set_list):
        logger.info("...")
        logger.debug("last_picon_set: %s",
                     config.plugins.piconcockpit.last_picon_set.value)
        picon_list = []
        for picon_set in picon_set_list:
            if not picon_set.startswith('<meta'):
                info_list = picon_set.split(';')
                if len(info_list) >= 9:
                    dir_url = os.path.join(
                        config.plugins.piconcockpit.picon_server.value, info_list[0])
                    pic_url = os.path.join(
                        config.plugins.piconcockpit.picon_server.value, info_list[0], info_list[1])
                    date = info_list[2]
                    name = info_list[3]
                    satellite = info_list[4]
                    creator = info_list[5]
                    bit = (info_list[6].replace(
                        ' ', '').lower()).replace('bit', ' bit')
                    size = info_list[7].replace(' ', '').lower()
                    uploader = info_list[8]
                    identifier = str(uuid.uuid4())
                    signature = "%s | %s - %s | %s | %s | %s" % (
                        satellite, creator, name, size, bit, uploader)
                    name = signature + " | %s" % date
                    if config.plugins.piconcockpit.satellite.value in ["all", satellite] and\
                            config.plugins.piconcockpit.creator.value in ["all", creator] and\
                            config.plugins.piconcockpit.size.value in ["all", size] and\
                            config.plugins.piconcockpit.bit.value in ["all", bit]:
                        picon_list.append(
                            ((name, dir_url, pic_url, identifier, signature), ))
        # logger.debug("picon_list: %s", picon_list)
        return picon_list

    def downloadPreview(self):
        logger.info("...")
        self["preview"].hide()
        if self['list'].getCurrent():
            logger.debug("current: %s", self["list"].getCurrent())
            url = self['list'].getCurrent()[2].replace(" ", "%20")
            logger.debug("url: %s", url)
            picon_path = os.path.join(
                "/tmp", self['list'].getCurrent()[3] + ".png")
            if not os.path.exists(picon_path):
                try:
                    downloadPage(url, picon_path).addCallback(
                        self.showPreview, picon_path).addErrback(self.showPreview, picon_path)
                except Exception as e:
                    logger.error("url: %s, e: %s", url, e)
            else:
                self.showPreview(None, picon_path)

    def showPreview(self, _result=None, path=None):
        logger.info("path: %s", path)
        self["preview"].show()
        self["preview"].instance.setPixmap(LoadPixmap(
            path, cached=False, size=self["preview"].instance.size()))
