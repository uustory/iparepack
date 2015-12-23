#!/usr/bin/env python3
# -*- coding:utf-8 -*-

#自定义处理脚本
def process(ipa_processor, appdir, infoPlist, channelConfig):
    sdkconfig = None
    if not 'U8SDK' in infoPlist:
        sdkconfig = {}
        infoPlist['U8SDK'] = sdkconfig
    else:
        sdkconfig = infoPlist['U8SDK']

    if 'channelId' in channelConfig:
        sdkconfig['Channel'] = int(channelConfig['channelId'])
    
    if 'U8SDK' in channelConfig:
        ipa_processor.merge_dict(infoPlist, {'U8SDK':channelConfig['U8SDK']})
    
    if 'CFBundleIdentifier' in channelConfig:
        infoPlist['CFBundleIdentifier'] = channelConfig['CFBundleIdentifier']
        
    if 'CFBundleDisplayName' in channelConfig:
        infoPlist['CFBundleDisplayName'] = channelConfig['CFBundleDisplayName']

