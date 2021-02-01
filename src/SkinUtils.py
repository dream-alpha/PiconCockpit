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
from Version import PLUGIN
from enigma import getDesktop
from skin import loadSkin, loadSingleSkinData, dom_skins
from Tools.Directories import fileExists, resolveFilename, SCOPE_SKIN, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS


def getSkinName(skin_name):
	width = getDesktop(0).size().width()
	if width == 1920:
		skinName = skin_name
	else:
		skinName = "NoSupport"
	return skinName


def getSkinPath(file_name):
	logger.debug("file_name: %s", file_name)
	skin_path = resolveFilename(SCOPE_CURRENT_SKIN, PLUGIN + "/skin/" + file_name)
	if not fileExists(skin_path):
		skin_path = resolveFilename(SCOPE_SKIN, "Default-FHD/" + PLUGIN + "/skin/" + file_name)
		if not fileExists(skin_path):
			skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/" + PLUGIN + "/skin/" + file_name)
	logger.debug("skin_path: %s", skin_path)
	return skin_path


def initPluginSkinPath():
	default_skin = resolveFilename(SCOPE_SKIN, "Default-FHD/" + PLUGIN)
	current_skin = resolveFilename(SCOPE_CURRENT_SKIN, PLUGIN)
	plugin_skin = resolveFilename(SCOPE_PLUGINS, "Extensions/" + PLUGIN)
	logger.info("current_skin: %s", current_skin)
	logger.info("default_skin: %s", default_skin)
	logger.info("plugin_skin: %s", plugin_skin)
	if not os.path.isdir(default_skin):
		logger.info("%s > %s", default_skin, plugin_skin)
		os.symlink(plugin_skin, default_skin)


def loadPluginSkin(skin_file):
	loadSkin(getSkinPath(skin_file), "")
	path, dom_skin = dom_skins[-1:][0]
	loadSingleSkinData(getDesktop(0), dom_skin, path)
