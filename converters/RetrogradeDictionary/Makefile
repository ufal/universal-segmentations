DATADIR=../../data
IN_DIR=$(DATADIR)/original/RetrogradeDictionary
OUT_DIR=$(DATADIR)/converted/ces-RetrogradeDictionary

SHELL = bash


download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	wget https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2546/slav_verbs.txt -O $(IN_DIR)/slav_verbs.txt

convert:
	mkdir -p $(OUT_DIR)
	python ./convert_morphs.py $(IN_DIR)/slav_verbs.txt $(OUT_DIR)/retrograde_dictionary.useg