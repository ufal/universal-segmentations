DATADIR=../../data/
IN_DIR=$(DATADIR)/original/CroDeriV/
OUT_DIR=$(DATADIR)/converted/hrv-CroDeriV/

SHELL = bash


all:
	mkdir -p $(OUT_DIR)
	$(MAKE) download
	$(MAKE) -s convert > $(OUT_DIR)conversion.log

download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	cd $(IN_DIR) && wget 'http://croderiv.ffzg.hr/Croderiv?p2=&p1=&root=&s2=&s1=&formString=*&pos=' -O 'webpage-data.html'

convert:
	mkdir -p $(OUT_DIR)
	./croderiv2useg.py $(IN_DIR)webpage-data.html manual-annotation.tsv $(OUT_DIR)CroDeriV.useg

clean:
	rm -rf $(IN_DIR)
	rm -rf $(OUT_DIR)
