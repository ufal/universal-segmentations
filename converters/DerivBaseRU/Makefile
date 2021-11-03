DATADIR=../../data/
IN_DIR=$(DATADIR)/original/DerivBaseRU/
OUT_DIR=$(DATADIR)/converted/rus-DerivBaseRU/

SHELL = bash


download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	cd $(IN_DIR) && wget https://github.com/s231644/DerivBaseRu/raw/master/data/wiktionary/v001.00-connections.zip
	unzip $(IN_DIR)v001.00-connections.zip -d $(IN_DIR)

convert:
	mkdir -p $(OUT_DIR)
	for file in $(IN_DIR)connections_adj.csv $(IN_DIR)connections_adv.csv $(IN_DIR)connections_noun.csv $(IN_DIR)connections_rare.csv $(IN_DIR)connections_special_verb.csv $(IN_DIR)connections_verb.csv ; do \
		./derivbaseru2useg.py $${file} $(OUT_DIR)$${file}.useg;\
	done
