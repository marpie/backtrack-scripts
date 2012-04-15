#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
""" nmap_new_hosts.py

    nmap_new_hosts compares two (or more) gnmap-files and prints the new 
    hosts of the second file.

    Author: marpie (marpie@a12d404.net)

    Last Update: 20120415
    Created:     20120415

"""
import argparse
from os.path import isfile

class Host(object):
    def __init__(self, rawData):
        self.rawData = rawData
        self.ip = ""
        self.dns = ""
        self.status = ""

    def __repr__(self):
        return self.rawData

    def __str__(self):
        return self.rawData

    def __eq__(self, other):
        return (self.ip == other.ip) and (self.status == other.status)

    def parse(self):
        if not self.rawData.startswith("Host: "):
            return None
        
        if not self.rawData.index("\t"):
            return None

        first, second = self.rawData.split("\t", 2)
        _, self.ip, dnsRaw = first.split(" ", 3)
        if not self.ip:
            return None
        self.dns = dnsRaw[1:-1]

        _, self.status = second.split(" ",2)

        return self

def readFile(fileName):
    with open(fileName, 'r') as f:
        for line in f:
            host = Host(line.strip()).parse()
            if host:
                yield host

def main(argv):
    parser = argparse.ArgumentParser(description="Diffs two (or more) gnmap-files to print the new hosts in the second file.")
    parser.add_argument("oldScan", type=str, help="first scan")
    parser.add_argument("newScan", type=str, nargs="+", help="next newer scan. The files need to be in scan order to produce meaningful results!")
    args = parser.parse_args()

    if not isfile(args.oldScan):
        print("'" + args.file1 + "' is not a file.")
        return False

    for filename in args.newScan:
        if not isfile(filename):
            print("'" + filename + "' is not a file.")
            return False

    # parse first scan
    hosts = []
    for host in readFile(args.oldScan):
        hosts.append(host)

    # compare with second scan
    alreadyPrinted = []
    for filename in args.newScan:
        for host in readFile(filename):
            if not (host in hosts) and not (host in alreadyPrinted):
                print(host)
                alreadyPrinted.append(host)

    return True

if __name__ == "__main__":
    import sys
    sys.exit(not main(sys.argv))


