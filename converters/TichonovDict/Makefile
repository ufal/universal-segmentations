DATADIR=../../data
OUT_DIR=$(DATADIR)/converted/rus-TichonovDict
SHELL = bash

convert:
	mkdir -p $(OUT_DIR)
	python ./convert_morphs.py $(DATADIR)/original/Tikhonov/tikhonov.txt $(OUT_DIR)/TichonovDict.useg