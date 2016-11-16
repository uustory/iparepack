#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import zipfile
import argparse
import os
import shutil
import sys
import plistlib
import json
import subprocess
import glob
import OpenSSL

from ipa_processor import IpaProcessor


def load_mobileprovision(provisionfile):
    with open(os.devnull, 'w') as devnull:
        plistcontent = subprocess.check_output("openssl smime -in \"%s\" -inform der -verify"%provisionfile, stderr=devnull, shell=True)
        return plistlib.loads(plistcontent)

def get_mobileprovision(name):
    for provisionfile in glob.glob(os.path.expanduser("~/Library/MobileDevice/Provisioning Profiles/*.mobileprovision")):
        plist = load_mobileprovision(provisionfile)
        if name == plist.get('Name'):
            return (plist,provisionfile)

    return (None,None)

def get_cert_cn(certBytes):
    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, certBytes)
    return cert.get_subject().commonName

def extractIpa(ipafile, workdir):
    zf = zipfile.ZipFile(ipafile, 'r')
    zf.extractall(workdir)
    zf.close()

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        if root != path:
            relroot = os.path.relpath(root, path)
            ziph.write(root, relroot)

        for file in files:
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, path)
            ziph.write(filepath, relpath, zipfile.ZIP_DEFLATED)


def repack(ipafile, appdir, outputdir, channelConfig, channelConfigDir):
    outputdir = os.path.abspath(outputdir)
    processor = IpaProcessor(appdir, channelConfig, channelConfigDir)
    processor.process()
    
    output_ipafile = ""
    if 'channelId' in channelConfig:
        output_ipafile = os.path.basename(ipafile.replace(".ipa", "_%s.ipa"%channelConfig['channelId'], 1))
    else:
        output_ipafile = os.path.basename(ipafile)

    print(channelConfig)
    if os.path.isfile("/usr/bin/codesign"):

        sign = None
        if 'provision' in channelConfig:
            provision = channelConfig['provision']

            if provision.endswith('.mobileprovision'):
                provisionfile = os.path.join(channelConfigDir, provision)
                shutil.copy2(provisionfile, os.path.join(appdir, "embedded.mobileprovision"))
            else:
                (provisionInfo,provisionfile) = get_mobileprovision(provision)
                if not provisionInfo:
                    print("cant find provision: \"%s\""%provision)
                    exit(-1)

                shutil.copy2(provisionfile, os.path.join(appdir, "embedded.mobileprovision"))
                sign = get_cert_cn(provisionInfo['DeveloperCertificates'][0])

        if not sign:
            provisionInfo = load_mobileprovision(os.path.join(appdir, "embedded.mobileprovision"))
            sign = get_cert_cn(provisionInfo['DeveloperCertificates'][0])

        if sign:
            print("\n\n\nPackageApplication \n \n");
            retValue = os.system("/usr/bin/codesign -vvvv -f -s \"%s\" --preserve-metadata=identifier,entitlements,resource-rules \"%s\""%(sign, appdir))
            if retValue != 0:
                exit(1)

    print("\n\npacking %s..."%os.path.join(outputdir, output_ipafile))
    if os.path.isfile("/usr/bin/xcrun"):
        os.system("/usr/bin/xcrun -sdk iphoneos PackageApplication -v \"%s\" -o \"%s\""%(appdir, os.path.join(outputdir, output_ipafile)))
    else:
        zf = zipfile.ZipFile(os.path.join(outputdir, output_ipafile), 'w')
        zipdir(workdir, zf)
        zf.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(sys.argv[0])

    parser.add_argument('inputfile', nargs='?', help=u'输入ipa文件路径')
    parser.add_argument('-c', '--config', help=u'配置文件')
    parser.add_argument('-o', '--output', help=u'输出目录')

    args = parser.parse_args()

    ipafile = "app.ipa"
    channelListFile = "channels.txt"

    if args.inputfile == None:
        pass
    elif args.inputfile.endswith('.ipa'):
        ipafile = args.inputfile
    elif args.inputfile.endswith('.txt'):
        channelListFile = args.inputfile

    basedir = os.path.dirname(channelListFile)
    workdir = os.path.join(basedir, 'workdir')
    if os.path.isdir(workdir):
        shutil.rmtree(workdir)
    os.mkdir(workdir)

    outputdir = args.output
    if not outputdir:
        outputdir = os.path.join(basedir, 'output')

    if not os.path.isdir(outputdir):
        os.makedirs(outputdir)

    print("正在解压%s..."%ipafile)
    extractIpa(ipafile, workdir)

    appdir = None
    for d in os.listdir(os.path.join(workdir, "Payload")):
        if d.endswith(".app"):
            appdir = os.path.join(workdir, "Payload", d)
            break

    if not appdir:
        print("找不到app")
        exit(-1)

    if args.config != None:
        configFile = args.config
        channelConfigDir = os.path.dirname(configFile)
        channelConfig = json.load(open(configFile, encoding='utf-8'))
        repack(ipafile, appdir, outputdir, channelConfig, channelConfigDir)
        exit(0)

    with open(channelListFile, "r", encoding='utf-8') as f:
        for line in f.readlines():
            channel = line.split(':', 1)
        
            channelId = channel[0].strip()
            #if args.channel and args.channel != channel[0].strip():
            #    continue

            channelConfig = {}
            channelConfigDir = None
            if len(channel) > 1:
                config = channel[1].strip()
                if config.startswith('{') and config.endswith('}'):
                    channelConfig = json.loads(config)
                else:
                    configFile = os.path.join(basedir, config)
                    channelConfigDir = os.path.dirname(configFile)
                    channelConfig = json.load(open(configFile, encoding='utf-8'))

                channelConfig['channelId'] = channelId

            repack(ipafile, appdir, outputdir, channelConfig, channelConfigDir)
