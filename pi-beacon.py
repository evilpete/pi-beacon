#!/usr/local/bin/python2.7

#!/usr/bin/env python


# pylint: disable=invalid-name
# global-statement,protected-access,invalid-name,missing-docstring,broad-except,too-many-branches,no-name-in-module

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
# import signal


import errno
#import signal
#import atexit

DEBUG = 0

# base_port = 54900

# udp_resend = True
PID_DIR = "/var/tmp"
pidpath = None

# signal.signal(signal.SIGCHLD, signal.SIG_IGN)
# current_milli_time = lambda: int(round(time.time() * 1000))

#start_milli_time = 0



LOC_DATA = """<root>
    <specVersion>
          <major>1</major>
          <minor>0</minor>
    </specVersion >
    <device>
        <deviceType>urn:schemas-upnp-org:device:Basic:1</deviceType>
        <friendlyName>{friendname}</friendlyName>
        <manufacturer>raapsberry pi</manufacturer>
        <manufacturerURL>https://www.raspberrypi.org/</manufacturerURL>
        <modelDescription>{modeldesc}</modelDescription>
        <modelName>{hardware}</modelName>
        <modelURL>https://www.raspberrypi.org/</modelURL>
        <modelNumber>{modelnumber}</modelNumber>
        <UDN>{uuid}</UDN>
        <UPC>???</UPC>
        <serialNumber>{serial}</serialNumber>
        <presentationURL>http://{ip_addr}/</presentationURL>
        <iconList>
            <icon>
                <mimetype>image/jpeg</mimetype>
                <width>64</width>
                <height>64</height>
                <depth>24</depth>
                <url>/icon.jpg</url>
            </icon>
        </iconList>
        <serviceList>
        </serviceList>
    </device>
</root>
"""

HTTP_ERR = """<html>
<head><title>404 Not Found</title></head>
<body><h1>404 Not Found</h1></body>
"""

ICON_DAT = """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
3Mdty1EqP6msgoAmq17pi5sfawm6tFFFFSsC/9k="""

MODELNAMES = {
    '0002' : "Model B Revision 1.0",
    '0003' : "Model B Revision 1.0 + ECN0001",

    '0004' : "Model B Revision 2.0 (256MB)",
    '0005' : "Model B Revision 2.0 (256MB)",
    '0006' : "Model B Revision 2.0 (256MB)",

    '0007' : "Model A",
    '0008' : "Model A",
    '0009' : "Model A",

    '000d' : "Model B Revision 2.0 (512MB)",
    '000e' : "Model B Revision 2.0 (512MB)",
    '000f' : "Model B Revision 2.0 (512MB)",
    # 700371902605

    '0010' : "Model B+",
    # 640522710164

    '0011' : "Compute Module",

    '0012' : "Model A+",
    # 702658303617

    'a01041' : "Pi 2 Model B (Sony, UK)",
    'a21041' : "Pi 2 Model B (Embest, China)"
    # Pi2 Pi640522710515

}

#def Exit_gracefully(signal, frame):
#    if DEBUG:
#        print "Exiting in a Graceful way"
#    b.send_notify(None, True)
#    b.send_notify("upnp:rootdevice", True)
#    sys.exit(0)



def grok(buf, skip=0):
    """
        Grok:  verb, informal
        understand (something) intuitively or by empathy
    """
    ret = dict()
    if skip:
        buflines = buf.split('\n')[skip:]
    else:
        buflines = buf.split('\n')

    for line in buflines:
        if not line:
            continue
        buf_list = line.split(':', 1)
        if len(buf_list) < 2:
            continue
        ky = buf_list[0].strip().upper()
        val = buf_list[1].strip()
        ret[ky] = val
    return ret

def cpuinfo():
    """
        Extract serial from cpuinfo file
    """
    try:
        # d = dict()
        with  open('/proc/cpuinfo', 'r') as fd:
            info = fd.read()
        ret = grok(info, 1)
    except Exception as _:
        return {}
    return ret


def meminfo():
    """
        Extract from /proc/meminfofile
    """
    try:
        ret = dict()
        with  open('/proc/meminfo', 'r') as fd:
            info = fd.read()
        ret = grok(info)
    except Exception as _:
        return {}
    return ret

def getmyip():
    """
        get IP address on host
    """
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.connect(("8.8.8.8", 53))
    myip = soc.getsockname()[0]
    soc.close()
    return myip


class pi_beacon(object):
    """
        A classy beacon pi
    """
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
        serial = self.hwinfo.get("SERIAL", "0000000000000000000")
        hardware = self.hwinfo.get("HARDWARE", "??")
        modelnum = self.hwinfo.get("REVISION", "??")
        modeldesc = MODELNAMES.get(modelnum, "??")

        self.perm_uuid = "RPI-1_0-" + serial

        self.url = "http://{0}:{1}/info.xml".format(self.myip, self.tport)
        self.data = LOC_DATA.format(hardware=hardware, uuid=self.perm_uuid,
                                    serial=serial, revision=modelnum,
                                    friendname=self.hostname,
                                    modelnumber=modelnum,
                                    modeldesc=modeldesc,
                                    ip_addr=self.myip)
        self.icon_dat = ICON_DAT.decode("base64")

        if DEBUG:
            print self.url
            print self.data

            print "UUID", self.uuid

        self.location_url = "http://{0}:{1}/info.xml".format(self.myip, self.tport)

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
        try:
            self.tsock.bind((self.myip, self.tport))
        except socket.error, err:
            print "IP/PORT=", self.myip, self.tport, err
            raise

        self.tsock.setblocking(0)
        self.tsock.listen(8)
        # self.tport = self.socket.getsockname()[1]

        self.infd.append(self.tsock)
        self.infd.append(self.usock)

    def poll(self):
        """
            poll for net connections
        """
        if DEBUG:
            print "infd:", len(self.infd), self.infd

        readfd, _, _ = select.select(self.infd, [], [], self.timeout)

        # print "readfd:", len(readfd), len(self.infd)
        # print "writefd:", len(writefd)
        # print "errfd:", len(errfd)

        for s in readfd:
            if s is self.tsock:
                if DEBUG:
                    print "tsock"
                client_sock, client_address = s.accept()
                client_sock.setblocking(0)
                self.infd.append(client_sock)
                continue
            elif s is self.usock:
                if DEBUG:
                    print "usock"
                self._handle_upnp(s)
                continue
            else:
                if DEBUG:
                    print "ssock #", s.fileno(), ":", len(self.infd)
                data, sender = s.recvfrom(1024)
                if not data:
                    self.infd.remove(s)
                    del s
                else:
                    self._handle_web(data, sender, s)


    def _handle_web(self, data, sender, s):
        """
            Handle web requests
        """
        if DEBUG:
            print "_handle_web"
            print "_handle_web ->", sender, "\n", data

        if data.startswith("GET /"):
            f = data.split(' ')[1]
            date_str = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)

            msg = ("HTTP/1.1 200 OK\r\n"
                   "CONTENT-LENGTH: {contlen}\r\n"
                   "CONTENT-TYPE: {conttype}\r\n"
                   "DATE: {curdate}\r\n"
                   "LAST-MODIFIED: Sat, 01 Jan 2000 00:01:15 GMT\r\n"
                   "SERVER: Unspecified, UPnP/1.0, Unspecified\r\n"
                   "X-User-Agent: redsonic\r\n"
                   "CONNECTION: close\r\n"
                   "\r\n"
                   "{msgdata}")

            if f == "/info.xml":
                message = msg.format(contlen=len(self.data),
                                     conttype="text/xml",
                                     curdate=date_str,
                                     msgdata=self.data)

            elif f == "/icon.jpg":
                message = msg.format(contlen=len(self.icon_dat),
                                     conttype="image/jpeg",
                                     curdate=date_str,
                                     msgdata=self.icon_dat)

            else:
                message = ("HTTP/1.1 404 Not Found\r\n"
                           "CONNECTION: close\r\n"
                           "Content-Length: {:d}\r\n"
                           "\r\n{:s}".format(len(HTTP_ERR), HTTP_ERR))
                if DEBUG:
                    print ">> 404 send"
                    print message


            try:
                s.send(message)
            except socket.error, err:
                if err.errno == errno.ECONNRESET:
                    print str(err)

        return

    def _handle_upnp(self, s):

        data, sender = s.recvfrom(1024)

        if sender[0] == self.myip:
            if DEBUG:
                print "_handle_upnp ->", sender
            return


        if data.startswith("M-SEARCH") is False:
            if DEBUG:
                # print "Unknown request:\n", data
                print "_handle_upnp skip", sender
            del data
            return
        else:
            if DEBUG:
                print "_handle_upnp", sender, "\n"# , data
            d = grok(data)
            if d['ST'] == "upnp:rootdevice":
                self._reply_upnp(sender, d['ST'], d['ST'])
            if d['ST'] == "ssdp:all":
                self._reply_upnp(sender, "uuid:" + self.perm_uuid, None)
                self._reply_upnp(sender, "upnp:rootdevice", "upnp:rootdevice")



    def _reply_upnp(self, sender, st, usn):
        if DEBUG:
            print "_reply_upnp", st, usn

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

        if DEBUG:
            print "=====\n", len(msguuid), "\n", msguuid, "->", sender, "\n\n"
        #self.usock.sendto(msguuid, sender)

        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.sendto(msguuid, sender)
        del temp_socket


    def send_notify(self, usn=None, byebye=False):
        """
            Send Upnp notify packet
        """
        if DEBUG:
            print "send_notify", usn

        reply_uuid = self.perm_uuid

        if usn is not None:
            reply_uuid = reply_uuid + "::" + usn
        else:
            usn = "uuid:" + self.perm_uuid

        if byebye:
            ntsstr = "ssdp:byebye"
        else:
            ntsstr = "ssdp:alive"



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

        if DEBUG:
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


beacon = pi_beacon()

try:
    pidpath = PID_DIR + "/pi-beacon.pid"
    with open(pidpath, 'w', 0644) as pfd:
        pfd.write("{}\n".format(os.getpid()))
except IOError as err:
    print "I/O error({0}): {1}".format(err.errno, err.strerror)
    pidpath = None
except Exception as err:
    print "Unexpected error:", pidpath, err
    pidpath = None

beacon.send_notify()
beacon.send_notify("upnp:rootdevice")

# signal.signal(signal.SIGINT, Exit_gracefully)
# signal.signal(signal.SIGKIL, Exit_gracefully)
while True:
    beacon.poll()
    if (int(time.time()) - beacon.lastnotify) > 240:
        beacon.send_notify()
        beacon.send_notify("upnp:rootdevice")
