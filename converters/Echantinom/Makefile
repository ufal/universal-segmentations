DATADIR=../../data/
IN_DIR=$(DATADIR)/original/Echantinom/
OUT_DIR=$(DATADIR)/converted/fra-Echantinom/

SHELL = bash


download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	cd $(IN_DIR) && wget https://osf.io/7phcy/download && mv download Echantinom.csv

convert:
	mkdir -p $(OUT_DIR)
	./fra_echantinom2useg.py $(IN_DIR)/Echantinom.csv  $(OUT_DIR)$/fra_echantinom.useg
