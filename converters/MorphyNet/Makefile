DATADIR=../../data/
IN_DIR=$(DATADIR)/original/MorphyNet/
OUT_DIR=$(DATADIR)/converted/

SHELL = bash


download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	git clone https://github.com/kbatsuren/MorphyNet $(IN_DIR)


convert:
#	mkdir -p $(OUT_DIR)
	./morphynet2useg.py $(IN_DIR) $(OUT_DIR)  | tee log.txt


