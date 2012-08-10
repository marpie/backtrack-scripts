#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" update_backtrack

    update_backtrack updates Metasploit and all repositories it can find.

    Author: marpie (marpie@a12d404.net)

    Last Update: 20120810
    Created:     20120322

"""
from os import listdir, getcwd, chdir
from os.path import join, isdir, isfile
from subprocess import call
from bz2 import decompress
from cStringIO import StringIO
import tarfile
import httplib

def updateGit(targetDir):
    return runProgInDir("git", "pull", targetDir)

def runProgInDir(cmd, arg, targetDir):
    oldDir = getcwd()
    if targetDir != "":
        chdir(targetDir)
    retCode = runProg(cmd, arg)
    chdir(oldDir)
    return retCode

def runProg(cmd, arg):
    retCode = False
    try:
        retCode = call(cmd + " " + arg, shell=True) == 0
    except OSError, e:
        pass
    return retCode

def get_repositories(baseDir, resultList):
    for entry in listdir(baseDir):
        fullPath = join(baseDir, entry)
        if not isdir(fullPath):
            continue
        isRepo = False
        for repo in VCS.keys():
            if isdir(join(fullPath, repo)):
                resultList.append((repo, fullPath,))
                isRepo = True
        if not isRepo:
            get_repositories(fullPath, resultList)

def update_exploitdb(directory):
    print("[U] Exploits Database by Offensive Security (exploit-db.com)")
    lastUpdate = None
    updateFile = join(directory, "last_update")
    if isfile(updateFile):
        with open(updateFile, "r") as f:
            lastUpdate = f.readline().strip()
        if len(lastUpdate) < 5:
            lastUpdate = None

    # checking current version
    print("[*] Checking current version...")
    http = httplib.HTTPConnection("www.exploit-db.com")
    http.request("HEAD", "/archive.tar.bz2")
    resp = http.getresponse()
    currentVersion = resp.getheader('last-modified').strip()
    resp.read()

    if lastUpdate != currentVersion:
        print("[!] new version available (" + currentVersion + ")")
        print("    loading new version...")
        http.request("GET", "/archive.tar.bz2")
        currentCompressed = http.getresponse().read()
        if not currentCompressed:
            print("[E] No data received from server!")
            return False
        currentUnpacked = decompress(currentCompressed)
        if not currentUnpacked:
            print("[E] Couldn't unpack bz2 data!")
            return False
        # extract archive
        tar = tarfile.open(fileobj=StringIO(currentUnpacked))
        tar.extractall(directory)
        tar.close()
        with open(updateFile, "w") as f:
            f.write(currentVersion)
        print("[X] exploit-db updated to version: " + currentVersion)
        return True
    else:
        print("[X] You already got the newest version! No update necessary.")
        return True
    print("[E] UNKNOWN ERROR!")
    return False

#
# VARs
#

DEFAULT_DIRS = (r'/pentest/',)
#       VCS    Update Command
VCS = { '.hg': "hg pull -u",
        '.git': updateGit,
        '.svn': "svn up",
}
SELF_UPDATING = {
        # Name:       (Path, Command,)
        'Metasploit': ('', 'msfupdate',),
        'OWASP Joomla! Vulnerability Scanner': ('/pentest/web/joomscan', '/pentest/web/joomscan/joomscan.pl update',),
        'OpenVAS': ('', 'openvas-nvt-sync'),
        'fimap': ('', '/pentest/web/fimap/fimap.py --update-def'),
        'Nmap OS Detection DB': ('/usr/local/share/nmap', 'wget http://nmap.org/svn/nmap-os-db -O nmap-os-db',),
        'Nmap Services DB': ('/usr/local/share/nmap', 'wget http://nmap.org/svn/nmap-services -O nmap-services',),
}



def main(argv):
    dirs = DEFAULT_DIRS

    print("[*] Running apt-get update, upgrade, dist-upgrade...")
    if not(runProg("apt-get", "update") and runProg("apt-get", "upgrade") and runProg("apt-get", "dist-upgrade")):
        print("[E] Error while updating system...")
        raw_input("\nPress [Enter] to continue...")

    print("[*] Searching for VCS directories...")
    resultList = []
    for dEntry in dirs:
        get_repositories(dEntry, resultList)
    
    print("[*] Starting Update...")
    for system, path in resultList:
        print("[U] Updating " + path)
        if type(VCS[system]) == str:
            runProg(VCS[system], path)
        else:
            VCS[system](path)
    
    print("[*] Starting update of 'self updating' tools...")
    for name in SELF_UPDATING.keys():
        print("[U] Updating " + name)
        runProgInDir(SELF_UPDATING[name][1], "", SELF_UPDATING[name][0])

    # update exploit-db.com
    if not update_exploitdb("/pentest/exploits/exploitdb"):
        print("Error while updating exploit-db!")
    
    print("All updates completed.")
    return True

if __name__ == "__main__":
    import sys
    print(__doc__)
    sys.exit(not main(sys.argv))

