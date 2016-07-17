
all: syntax

BINDIR=/var/lib/pi-beacon/

syntax:
	python -m py_compile pi-beacon.py

install:
	 cp pi-beacon-start /etc/init.d/
	 chmod 755 /etc/init.d/pi-beacon-start
	 mkdir -p ${BINDIR}
	 cp pi-beacon.py  ${BINDIR}
	 chmod 755 ${BINDIR}/pi-beacon.py
