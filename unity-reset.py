#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Authors:
#   J Phani Mahesh <phanimahesh@gmail.com>
#   Barneedhar (jokerdino) <barneedhar@ubuntu.com>
#   Amith KK <amithkumaran@gmail.com>
#
# Description:
#   Python wrapper to reset unity.
#   Born at http://chat.stackexchange.com/rooms/6118/unity-reconfiguration
#
# Legal Stuff:
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUTa
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import subprocess
from gi.repository import Gio
import re

class UnityReset():
    allSchemas=Gio.Settings.list_schemas()
    allRelocatableSchemas=Gio.Settings.list_relocatable_schemas()
    
    def __init__(self):
        print "Initialising Unity reset"
        print "Killing Unity and Compiz"
        subprocess.call(["killall","unity-panel-service"])
        subprocess.call(["pkill","-9","compiz"])
        print "Resetting compiz plugins"
        self.resetPlugins()
        print "Resetting Unity settings"
        self.resetUnityChildren()
        print "Reset complete. Reloading unity"
        subprocess.call("unity")

    def resetAllKeys(self,schema,path=None):
        """Reset all keys in given Schema."""
        if (schema not in self.allSchemas) and (schema not in self.allRelocatableSchemas):
            print "Ignoring missing Schema %s"%schema
            return
        gsettings=Gio.Settings(schema=schema,path=path)
        for key in gsettings.list_keys():
            gsettings.reset(key)
        gsettings.apply()
        print "Schema %s successfully reset"%schema

    def resetPlugins(self):
        """Reset Compiz Plugins"""
        compizPluginRe=re.compile(r'(?P<plugin>org.compiz.)')
        for schema in self.allRelocatableSchemas:
            if compizPluginRe.match(schema):
                plugin=compizPluginRe.sub('',schema)
                schema='org.compiz.'+plugin
                path="/org/compiz/profiles/unity/plugins/"+plugin+"/"
                self.resetAllKeys(schema=schema,path=path)

    def resetUnityChildren(self):
        """Reset keys in child schemas of Unity"""
        unitySchema='com.canonical.Unity'
        blacklists=['com.canonical.Unity.Launcher','com.canonical.Unity.webapps','com.canonical.Unity.Lenses']
        unityChildRe=re.compile(unitySchema)
        for schema in self.allSchemas:
            if (schema not in blacklists) and (unityChildRe.match(schema)):
                self.resetAllKeys(schema)
    
    def getAllKeys(self,schema,path=None):
        """Snapshot current settings in a given schema"""
        if (schema not in self.allSchemas) and (schema not in self.allRelocatableSchemas):
            print "Ignoring missing Schema %s"%schema
            return
        snapshot=dict()
        gsettings=Gio.Settings(schema=schema,path=path)
        for key in gsettings.list_keys():
            snapshot[key]=gsettings.get_value(key)
        return snapshot
        
    def snapshotCompizPlugins(self):
        """Snapshot compiz plugins"""
        snapshot=dict()
        compizPluginRe=re.compile(r'(?P<plugin>org.compiz.)')
        for schema in self.allRelocatableSchemas:
            if compizPluginRe.match(schema):
                plugin=compizPluginRe.sub('',schema)
                schema='org.compiz.'+plugin
                path="/org/compiz/profiles/unity/plugins/"+plugin+"/"
                snapshot[schema]=self.getAllKeys(schema=schema,path=path)
        return snapshot

    def snapshotUnityChildren(self):
        """Snapshot keys in child schemas of Unity"""
        snapshot=dict()
        unitySchema='com.canonical.Unity'
        blacklists=['com.canonical.Unity.Launcher','com.canonical.Unity.webapps','com.canonical.Unity.Lenses']
        unityChildRe=re.compile(unitySchema)
        for schema in self.allSchemas:
            if (schema not in blacklists) and (unityChildRe.match(schema)):
                snapshot[schema]=self.getAllKeys(schema)
        return snapshot
        

if __name__=='__main__':
    UnityReset()

