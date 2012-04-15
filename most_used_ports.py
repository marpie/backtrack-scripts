#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
""" most_used_ports

    most_used_ports uses the Nmap services file to filter the N most 
    commonly used ports for a given protocol.

    Author: marpie (marpie@a12d404.net)

    Last Update: 20120415
    Created:     20120414

"""
import argparse
from os.path import isfile

NMAP_SERVICES_FILE = "/usr/local/share/nmap/nmap-services"

class Service(object):
    def __init__(self, rawData):
        self.rawData = rawData
        self.serviceName = ""
        self.port = ""
        self.protocol = ""
        self.openFrequency = 0.0
        self.comment = ""
    
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "\t".join((self.protocol, self.port, self.serviceName, str(self.openFrequency), self.comment,))

    def parse(self):
        """ parse returns "self" on success. """
        if self.rawData.startswith("#"):
            return None
        fields = self.rawData.split("\t")
        if len(fields) < 3:
            return None
        
        if len(fields) > 3:
            self.comment = '\t'.join(fields[3:])

        self.serviceName = fields[0]
        if not fields[1].index("/"):
            return None
        self.port, self.protocol = fields[1].split("/", 2)
        self.openFrequency = float(fields[2])

        return self

def readFile(fileName):
    services = []
    with open(fileName, 'r') as f:
        for line in f:
            service = Service(line.strip()).parse()
            if service:
                services.append(service)
    return services

def filterByProtocol(services, protocol = "tcp"):
    return filter(lambda service: service.protocol == protocol, services)

def sortByFrequency(services):
    services = sorted(services, key=lambda service: service.openFrequency)
    services.reverse()
    return services

def main(argv):
    if not isfile(NMAP_SERVICES_FILE):
        print("Nmap services file not found.")
        return False
    
    parser = argparse.ArgumentParser(description="Enumerates the N most commonly used ports for a given protocol.")
    parser.add_argument("N", metavar="N", type=int, help="Number of ports to return")
    parser.add_argument("--only", metavar="PROTO", dest="only", nargs=1, default=None, help="If set only the given protocol is returned.")
    args = parser.parse_args()

    services = sortByFrequency(readFile(NMAP_SERVICES_FILE))

    if args.only:
        try:
            services = filterByProtocol(services, args.only[0].lower())[:args.N]
        except:
            print("Protocol '%s' not found!" % args.only)
            return False
        
        for service in services:
            print(service)

        return True

    print(__doc__)
    print("Enumerating the %d most commonly used ports ..." % args.N)

    for protocol in ("tcp", "udp", "sctp",):
        try:
            newServices = filterByProtocol(services, protocol)[:args.N]
        except:
            print("Protocol '%s' not found!" % protocol)
            continue

        print("\n[%s Ports]" % protocol.upper())
        for service in newServices:
            print(service)
    
    return True

if __name__ == "__main__":
    import sys
    sys.exit(not main(sys.argv))


