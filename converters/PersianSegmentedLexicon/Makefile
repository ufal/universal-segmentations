DATADIR=../../data/
IN_DIR=$(DATADIR)/original/PersianMorphSegLex/
OUT_DIR=$(DATADIR)/converted/fa-PersianMorphSegLex/

SHELL = bash


download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	cd $(IN_DIR) && curl --remote-name-all -O https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3011{/readme.txt,/train.txt,/dev.txt,/test.txt}

convert:
	mkdir -p $(OUT_DIR)
	for FILE in train dev test ; do \
	    ./persian2useg.py $(IN_DIR)$${FILE}.txt  $(OUT_DIR)$${FILE}.useg ; \
	done

