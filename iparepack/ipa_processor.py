#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import collections
import plistlib
import process_script
import os

class IpaProcessor:
    def __init__(self, appdir, channelConfig, channelConfigDir):
        self.appdir = appdir
        self.channelConfig = channelConfig
        self.channelConfigDir = channelConfigDir
        
        infoplistfile = os.path.join(appdir, "Info.plist")
        self.infoPlist = plistlib.load(open(infoplistfile, "rb"))
    
    @staticmethod
    def merge_dict(d1, d2):
        """
        Modifies d1 in-place to contain values from d2.  If any value
        in d1 is a dictionary (or dict-like), *and* the corresponding
        value in d2 is also a dictionary, then merge them in-place.
        """
        for k,v2 in d2.items():
            v1 = d1.get(k) # returns None if v1 has no value for this key
            if (isinstance(v1, collections.Mapping) and
                isinstance(v2, collections.Mapping) ):
                IpaProcessor.merge_dict(v1, v2)
            else:
                d1[k] = v2
                
    def launch_script(self, scriptfile):
        processScript = {}
        with open(scriptfile, encoding='utf-8') as f:
            exec(f.read(), {}, processScript)

        processScript['process'](self, self.appdir, self.infoPlist, self.channelConfig)

    def process(self):
        self.launch_script(os.path.join(os.path.dirname(__file__), 'process_script.py'))
        
        if self.channelConfigDir:
            channelProcessScript = os.path.join(self.channelConfigDir, "process_script.py")
            if (os.path.isfile(channelProcessScript)):
                self.launch_script(channelProcessScript)
        
        infoplistfile = os.path.join(self.appdir, "Info.plist")
        plistlib.dump(self.infoPlist, open(infoplistfile, "wb"), fmt = plistlib.FMT_BINARY)