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


from Components.config import config
from .Debug import logger
from .__init__ import _


class ConfigScreenInit():
    def __init__(self, _csel, session):
        self.session = session
        self.section = 400 * "¯"
        # text, config, on save, on ok, e2 usage level, depends on rel parent, description
        self.config_list = [
            (self.section, _("COCKPIT"), None, None, 0, [], ""),
            (_("Picon directory"), config.usage.configselection_piconspath, self.validatePath,
             None, 0, [], _("Select the directory the picons are stored in.")),
            (_("Picon server"), config.plugins.piconcockpit.picon_server,
             None, None, 0, [], _("Select the picon server.")),
            (_("Download all picons"), config.plugins.piconcockpit.all_picons, None, None, 0, [
            ], _("Should all picons be downloaded vs. just the picons in favorites?")),
            (_("Delete picon directory"), config.plugins.piconcockpit.delete_before_download,
             None, None, 0, [], _("Should the picon directory be cleaned before the download?")),
            (self.section, _("FILTER"), None, None, 0, [], ""),
            (_("Satellite"), config.plugins.piconcockpit.satellite,
             None, None, 0, [], _("Select the satellite.")),
            (_("Creator"), config.plugins.piconcockpit.creator,
             None, None, 0, [], _("Select the creator.")),
            (_("Size"), config.plugins.piconcockpit.size,
             None, None, 0, [], _("Select the picon size.")),
            (_("Color depth"), config.plugins.piconcockpit.bit,
             None, None, 0, [], _("Select the color depth.")),
            (self.section, _("DEBUG"), None, None, 2, [], ""),
            (_("Log level"), config.plugins.piconcockpit.debug_log_level,
             self.setLogLevel, None, 2, [], _("Select the debug log level.")),
        ]

    @staticmethod
    def save(_conf):
        logger.debug("...")

    def openLocationBox(self, element):
        logger.debug("element: %s", element.value)
        return True

    def setLogLevel(self, element):
        logger.debug("element: %s", element.value)
        return True

    def validatePath(self, element):
        logger.debug("element: %s", element.value)
        return True
