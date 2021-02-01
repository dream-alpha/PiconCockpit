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
import shutil
from pipes import quote


def readFile(path):
	try:
		f = open(path, "r")
		data = f.read()
		f.close()
		return data
	except Exception as e:
		logger.info("path: %s, exception: %s", path, e)
		return ""


def writeFile(path, data):
	try:
		f = open(path, "w")
		f.write(data)
		f.close()
	except Exception as e:
		logger.error("path: %s, exception: %s", path, e)


def deleteFile(path):
	try:
		os.remove(path)
	except Exception as e:
		logger.error("exception: path: %s, exception: %s", path, e)


def touchFile(path):
	try:
		os.popen("touch " + quote(path))
	except Exception as e:
		logger.error("exception: path: %s, exception: %s", path, e)


def copyFile(src_path, dest_path):
	try:
		shutil.copyfile(src_path, dest_path)
	except Exception as e:
		logger.error("exception: src_path: %s, dest_path: %s, exception: %s", src_path, dest_path, e)


def createDirectory(path):
	rc = 0
	result = os.popen("mkdir -p %s" % quote(path)).read()
	if result:
		rc = 1
	return rc


def deleteDirectory(path):
	try:
		shutil.rmtree(path)
	except Exception as e:
		logger.error("exception: path: %s, exception: %s", path, e)
