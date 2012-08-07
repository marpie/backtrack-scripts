#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" update_backtrack

    update_backtrack updates Metasploit and all repositories it can find.

    Author: marpie (marpie@a12d404.net)

    Last Update: 20120807
    Created:     20120322

"""
from os import listdir, getcwd, chdir
from os.path import join, isdir
from subprocess import call

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
    
    print("All updates completed. Please run 'apt-get update && apt-get upgrade && apt-get dist-upgrade' now.")
    return True

if __name__ == "__main__":
    import sys
    print(__doc__)
    sys.exit(not main(sys.argv))


