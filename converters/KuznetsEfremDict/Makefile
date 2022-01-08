DATADIR=../../data/
IN_DIR=$(DATADIR)/original/KuznetsEfremDict/
OUT_DIR=$(DATADIR)/converted/rus-KuznetsEfremDict/

SHELL = bash


all:
	mkdir -p $(OUT_DIR)
	$(MAKE) download
	$(MAKE) -s convert > $(OUT_DIR)conversion.log

download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	cd $(IN_DIR) && wget https://raw.githubusercontent.com/olesar/Reproducible-Research/master/ruWordFormation/morphodictKE1985.txt

convert:
	mkdir -p $(OUT_DIR)
	./dictofrusmorph2useg.py $(IN_DIR)morphodictKE1985.txt $(OUT_DIR)KuznetsEfremDict.useg > $(OUT_DIR)conversion.log

clean:
	rm -rf $(IN_DIR)
	rm -rf $(OUT_DIR)
