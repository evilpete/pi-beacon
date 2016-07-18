
all: syntax

BINDIR=/var/lib/pi-beacon/

syntax:
	python -m py_compile pi-beacon.py

install: syntax install-script install-systemd

install-oldinit:
	 cp pi-beacon-start /etc/init.d/pi-beacon
	 chmod 755 /etc/init.d/pi-beacon
	 update-rc.d pi-beacon defaults
	 update-rc.d pi-beacon enable

install-script:
	 mkdir -p ${BINDIR}
	 cp pi-beacon.py  ${BINDIR}
	 chmod 755 ${BINDIR}/pi-beacon.py

install-systemd:
	cp pi-beacon.service /lib/systemd/system/
	chmod 644  /lib/systemd/system/pi-beacon.service

# test -d /lib/systemd/system && ln -sf /dev/null /lib/systemd/system/pi-beacon.service

uninstall:
	 -update-rc.d pi-beacon disable
	 -rm -f /lib/systemd/system/pi-beacon.service
	 -rm -f /etc/init.d/pi-beacon
	 -rm -f /etc/rc?.d/[SK]??pi-beacon

