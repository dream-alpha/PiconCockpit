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


from Components.config import config, ConfigText, ConfigYesNo, ConfigSelection, ConfigSubsection, ConfigNothing, NoSave
from .Debug import logger, log_levels, initLogging


server_choices = [
    ("http://picons.vuplus-support.org/", "vuplus-support.org"),
]


class ConfigInit():

    def __init__(self, size_list=None, bit_list=None, creator_list=None, satellite_list=None):
        logger.debug("...")
        select_all = ["all"]
        if size_list is None:
            size_list = select_all
        if bit_list is None:
            bit_list = select_all
        if creator_list is None:
            creator_list = select_all
        if satellite_list is None:
            satellite_list = select_all

        config.plugins.piconcockpit = ConfigSubsection()
        config.plugins.piconcockpit.fake_entry = NoSave(ConfigNothing())
        config.plugins.piconcockpit.picon_server = ConfigSelection(
            default=server_choices[0][0], choices=server_choices)
        config.plugins.piconcockpit.size = ConfigSelection(
            default="all", choices=size_list)
        config.plugins.piconcockpit.bit = ConfigSelection(
            default="all", choices=bit_list)
        config.plugins.piconcockpit.creator = ConfigSelection(
            default="all", choices=creator_list)
        config.plugins.piconcockpit.satellite = ConfigSelection(
            default="all", choices=satellite_list)
        config.plugins.piconcockpit.last_picon_set = ConfigText(
            default="", fixed_size=False, visible_width=20)
        config.plugins.piconcockpit.all_picons = ConfigYesNo(default=False)
        config.plugins.piconcockpit.delete_before_download = ConfigYesNo(
            default=False)
        config.plugins.piconcockpit.debug_log_level = ConfigSelection(
            default="INFO", choices=list(log_levels.keys()))
        initLogging()
