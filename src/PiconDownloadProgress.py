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
from twisted.web.client import downloadPage
from .Debug import logger
from .__init__ import _
from .FileProgress import FileProgress
from .DelayTimer import DelayTimer
from .SkinUtils import getSkinName


class PiconDownloadProgress(FileProgress):

    def __init__(self, session, picon_set_url, picons, picon_dir):
        logger.debug("...")
        self.picon_set_url = picon_set_url
        self.picons = picons
        self.picon_dir = picon_dir
        FileProgress.__init__(self, session)
        self.skinName = getSkinName("PiconDownloadProgress")
        self.setTitle(_("Picon Download") + " ...")
        self.execution_list = []
        self.onShow.append(self.onDialogShow)

    def onDialogShow(self):
        logger.debug("...")
        self.execPiconDownloadProgress()

    def doFileOp(self, entry):
        picon = entry
        self.file_name = picon
        self.status = _("Please wait") + " ..."
        self.updateProgress()
        url = os.path.join(self.picon_set_url, picon).replace(" ", "%20")
        download_file = os.path.join(self.picon_dir, picon)
        logger.debug("url: %s, download_file: %s", url, download_file)
        downloadPage(url, str(download_file)).addCallback(
            self.downloadSuccess).addErrback(self.downloadError, url)

    def downloadSuccess(self, _result=None):
        # logger.info("...")
        self.nextFileOp()

    def downloadError(self, result, url):
        logger.info("url: %s, result: %s", url, result)
        self.nextFileOp()

    def execPiconDownloadProgress(self):
        logger.debug("...")
        self.status = _("Initializing") + " ..."
        self.updateProgress()
        self.execution_list = self.picons
        self.total_files = len(self.execution_list)
        DelayTimer(10, self.nextFileOp)
