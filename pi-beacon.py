#!/usr/local/bin/python2.7

#!/usr/bin/env python



# "alexa  Discover my devices"
# For a complete discussion, see http://www.makermusings.com

import email.utils
# import requests
import select
import socket
import struct
#import sys
import time
#import urllib
import uuid
import os
#import datetime
import signal


import errno
#import signal
#import atexit

debug = 0


base_port = 54900

udp_resend=True

# signal.signal(signal.SIGCHLD, signal.SIG_IGN)
current_milli_time = lambda: int(round(time.time() * 1000))

start_milli_time = 0



loc_data = """<root>
    <device>
        <deviceType>urn:schemas-upnp-org:device:Basic:1</deviceType>
        <friendlyName>{friendname}</friendlyName>
        <manufacturer>rasberry pi</manufacturer>
        <manufacturerURL>https://www.raspberrypi.org/</manufacturerURL>
        <modelName>{hardware}</modelName>
        <modelURL>https://www.raspberrypi.org/</modelURL>
        <modelNumber>{modelnumber}</modelNumber>
        <UDN>{uuid}</UDN>
        <serialNumber>{serial}</serialNumber>
        <presentationURL>http://{ip_addr}/</presentationURL>
    </device>
</root>
"""

http_err = """<html>
<head><title>404 Not Found</title></head>
<body><h1>404 Not Found</h1></body>
"""

#def Exit_gracefully(signal, frame):
#    if debug:
#        print "Exiting in a Graceful way"
#    b.send_notify(None, True)
#    b.send_notify("upnp:rootdevice", True)
#    sys.exit(0)



def grok(buf, skip=0):
    r = dict()
    if skip:
        buflines = buf.split('\n')[skip:]
    else:
        buflines = buf.split('\n')

    for line in buflines:
        if not line:
            continue
        a = line.split(':', 1)
        if len(a) < 2:
            continue
        k = a[0].strip().upper()
        v = a[1].strip()
        r[k] = v
    return r

def cpuinfo():
    # Extract serial from cpuinfo file
    try:
        # d = dict()
        with  open('/proc/cpuinfo', 'r') as f:
            b = f.read()
        d = grok(b, 1)
    except:
        return {}
    return d


def meminfo():
    # Extract from /proc/meminfofile
    try:
        d = dict()
        with  open('/proc/meminfo', 'r') as f:
            b = f.read()
        d = grok(b)
    except:
        return {}
    return d

def getmyip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 53))
    myip = s.getsockname()[0]
    s.close()
    return myip


class pi_beacon(object):

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.myip = getmyip()
        self.uip = '239.255.255.250'
        # self.mip = '10.1.1.255'
        self.uport = 1900
        self.tport = 44444
        self.uuid = str(uuid.uuid1(uuid.getnode(), 0))
        self.server_version = "Unspecified, UPnP/1.0, Unspecified"
        self.hostname = os.uname()[1]
        self.lastnotify = 0

        #load_age = ":".join(str(x) for x in os.getloadavg())


        self.hwinfo = cpuinfo()
        serial = self.hwinfo.get("SERIAL", "0000000000000000")
        hardware = self.hwinfo.get("HARDWARE", "??")
        modelnum = self.hwinfo.get("REVISION", "??")

        self.perm_uuid = "Socket-1_0-" + serial

        self.url = "http://{0}:{1}/info.xml".format(self.myip, self.tport)
        self.data = loc_data.format(hardware=hardware, uuid=self.perm_uuid,
                                    serial=serial, revision=modelnum,
                                    friendname=self.hostname,
                                    modelnumber=modelnum,
                                    ip_addr=self.myip)

        if debug:
            print self.url
            print self.data

            print "UUID", self.uuid

        self.location_url = "http://{0}/upnpxml/rpi.xml".format(self.myip)

        self.infd = []

        mreq = struct.pack("=4sl", socket.inet_aton("239.255.255.250"), socket.INADDR_ANY)

        #Set up UDP reciver socket
        self.usock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.usock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.usock.setblocking(0)
        self.usock.bind(('', self.uport))
        self.usock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.usock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


        self.tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tsock.bind((self.myip, self.tport))
        self.tsock.setblocking(0)
        self.tsock.listen(8)
        # self.tport = self.socket.getsockname()[1]

        self.infd.append(self.tsock)
        self.infd.append(self.usock)

    def poll(self):

        if debug:
            print "infd:", len(self.infd), self.infd

        readfd, writefd, errfd = select.select(self.infd, [], [], self.timeout)

        # print "readfd:", len(readfd), len(self.infd)
        #print "writefd:", len(writefd)
        #print "errfd:", len(errfd)

        for s in readfd:
            if s is self.tsock:
                if debug:
                    print "tsock"
                client_sock, client_address = s.accept()
                client_sock.setblocking(0)
                self.infd.append(client_sock)
                continue
            elif s is self.usock:
                if debug:
                    print "usock"
                self.handle_upnp(s)
                continue
            else:
                if debug:
                    print "ssock #", s.fileno(), ":", len(self.infd)
                data, sender = s.recvfrom(1024)
                if not data:
                    self.infd.remove(s)
                    del s
                else:
                    self.handle_web(data, sender, s)


    def handle_web(self, data, sender, s):
        if debug:
            print "handle_web"
            print "handle_web ->", sender, "\n", data

        if data.startswith("GET /"):
            f = data.split(' ')[1]

            if f != "/info.xml":
                if debug:

                    print ">> 404 send"
                message = ("HTTP/1.1 404 Not Found\r\n"
                           "CONNECTION: close\r\n"
                           "Content-Length: {:d}\r\n"
                           "\r\n{:s}".format(len(http_err), http_err))
                if debug:
                    print message
            else:
                date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
                message = ("HTTP/1.1 200 OK\r\n"
                          "CONTENT-LENGTH: {contlend}\r\n"
                          "CONTENT-TYPE: text/xml\r\n"
                          "DATE: {curdate}\r\n"
                          "LAST-MODIFIED: Sat, 01 Jan 2000 00:01:15 GMT\r\n"
                          "SERVER: Unspecified, UPnP/1.0, Unspecified\r\n"
                          "X-User-Agent: redsonic\r\n"
                          "CONNECTION: close\r\n"
                          "\r\n"
                          "{msgdata}".format(contlend=len(self.data),
                                             curdate=date_str,
                                             msgdata=self.data))
	    try:
		s.send(message)
	    except socket.error, e:
		if e.errno == errno.ECONNRESET:
		    print str(e)

        return

    def handle_upnp(self, s):

        data, sender = s.recvfrom(1024)

        if sender[0] == self.myip:
            if debug:
                print "handle_upnp ->", sender
            return


        if data.startswith("M-SEARCH") == False:
            if debug:
                # print "Unknown request:\n", data
                print "handle_upnp skip", sender
            del data
            return
        else:
            if debug:
                print "handle_upnp", sender, "\n"# , data
            d = grok(data)
            if d['ST'] == "upnp:rootdevice":
                self.reply_upnp(sender, d['ST'], d['ST'])
            if d['ST'] == "ssdp:all":
                self.reply_upnp(sender, "uuid:" + self.perm_uuid, None)
                self.reply_upnp(sender, "upnp:rootdevice", "upnp:rootdevice")



    def reply_upnp(self, sender, st, usn):
        if debug:
            print "reply_upnp", st, usn

        date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
        reply_uuid = self.perm_uuid
        if usn is not None:
            reply_uuid = reply_uuid + "::" + usn


        msguuid = ("HTTP/1.1 200 OK\r\n"
                  "CACHE-CONTROL: max-age=300\r\n"
                  "DATE: {CurDate}\r\n"
                  "EXT:\r\n"
                  "LOCATION: {LocationUrl}\r\n"
                  "OPT: \"http://schemas.upnp.org/upnp/1/0/\"; ns=01\r\n"
                  "SERVER: {ServerInfo}\r\n"
                  "X-User-Agent: redsonic\r\n"
                  "ST: {SearchTarget}\r\n"
                  "USN: uuid:{UniqueServiceName}\r\n"
                  "01-NLS: {NetLocSig}\r\n"
                  "Content-Length: 0\r\n"
                  "\r\n".format(CurDate=date_str, LocationUrl=self.location_url,
                                ServerInfo=self.server_version,
                                SearchTarget=st, UniqueServiceName=reply_uuid, NetLocSig=self.uuid))

        if debug:
            print "=====\n", len(msguuid), "\n", msguuid, "->", sender, "\n\n"
        #self.usock.sendto(msguuid, sender)

        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.sendto(msguuid, sender)
        del temp_socket


    def send_notify(self, usn=None, byebye=False):

        if debug:
            print "send_notify", usn

        reply_uuid = self.perm_uuid

        if usn is not None:
            reply_uuid = reply_uuid + "::" + usn
        else:
            usn = "uuid:" + self.perm_uuid

        if byebye: 
            ntsstr="ssdp:byebye"
        else:
            ntsstr="ssdp:alive"



                  # "01-NLS: {!s}\r\n"
                  # "OPT: \"http://schemas.upnp.org/upnp/1/0/\"; ns=01\r\n"
                  # "X-User-Agent: redsonic\r\n"
        msgssdp = ("NOTIFY * HTTP/1.1\r\n"
                    "HOST: 239.255.255.250:1900\r\n"
                    "CACHE-CONTROL: max-age=300\r\n"
                    "LOCATION: {LocationUrl}\r\n"
                    "NT: {NotificationType}\r\n"
                    "NTS: {NtsStr}\r\n"
                    "SERVER: {ServerInfo}\r\n"
                    "USN: uuid:{UniqueServiceName}\r\n"
                    "\r\n".format(
                        LocationUrl=self.url,
                        NotificationType=usn,
                        NtsStr=ntsstr,
                        ServerInfo=self.server_version,
                        UniqueServiceName=reply_uuid))
                        # self.uuid

        if debug:
            print "=====\n", len(msgssdp), "\n", msgssdp, "->", ('239.255.255.250', 1900), "\n\n"

        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.sendto(msgssdp, ('239.255.255.250', 1900))
        del temp_socket

        self.lastnotify = int(time.time())

        # self.usock.sendto(msgssdp, (self.uip, self.uport))

#       msgroot = ("NOTIFY * HTTP/1.1\r\n"
#                 "HOST: 239.255.255.250:1900\r\n"
#                 "CACHE-CONTROL: max-age=300\r\n"
#                 "LOCATION: {!s}\r\n"
#                 "NT: {!s}\r\n"
#                 "NTS: ssdp:alive\r\n"
#                 "X-User-Agent: redsonic\r\n"
#                 "SERVER: {!s}\r\n"
#                 "USN: uuid:{!s}\r\n"
#                 "\r\n".format(
#                         self.url,
#                         "upnp:rootdevice",
#                         self.server_version,
#                         reply_uuid))


b = pi_beacon()


b.send_notify()
b.send_notify("upnp:rootdevice")

# signal.signal(signal.SIGINT, Exit_gracefully)
# signal.signal(signal.SIGKIL, Exit_gracefully)

while True:
    b.poll()
    if (int(time.time()) - b.lastnotify) > 240 :
        b.send_notify()
        b.send_notify("upnp:rootdevice")


