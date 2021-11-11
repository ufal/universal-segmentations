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
	./derivbaseru2useg.py <(cat <(tail -n +2 $(IN_DIR)connections_adj.csv) <(tail -n +2 $(IN_DIR)connections_adv.csv) <(tail -n +2 $(IN_DIR)connections_noun.csv) <(tail -n +2 $(IN_DIR)connections_rare.csv) <(tail -n +2 $(IN_DIR)connections_special_verb.csv) <(tail -n +2 $(IN_DIR)connections_verb.csv)) $(OUT_DIR)DerivBaseRU.useg

	# for file in connections_adj.csv connections_adv.csv connections_noun.csv connections_rare.csv connections_special_verb.csv connections_verb.csv ; do \
	# 	./derivbaseru2useg.py <(tail -n +2 $(IN_DIR)$${file}) $(OUT_DIR)$${file}.useg;\
	# done
