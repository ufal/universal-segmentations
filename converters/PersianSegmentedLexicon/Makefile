DATADIR=../../data/
IN_DIR=$(DATADIR)/original/PersianMorphSegLex/
OUT_DIR=$(DATADIR)/converted/fas-PersianMorphSegLex/

SHELL = bash


download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	cd $(IN_DIR) && curl --remote-name-all -O https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3011{/readme.txt,/train.txt,/dev.txt,/test.txt}

convert:
	mkdir -p $(OUT_DIR)
	python ./persian2useg.py $(IN_DIR)train.txt $(IN_DIR)dev.txt $(IN_DIR)test.txt  $(OUT_DIR)fas-PersianMorphSegLex.useg

