DATADIR=../../data/
IN_DIR=$(DATADIR)/original/DerivBaseRU/
OUT_DIR=$(DATADIR)/converted/rus-DerivBaseRU/

SHELL = bash


all:
	mkdir -p $(OUT_DIR)
	$(MAKE) download
	$(MAKE) -s convert > $(OUT_DIR)conversion.log

download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	cd $(IN_DIR) && wget https://github.com/s231644/DerivBaseRu/raw/master/data/wiktionary/v001.00-connections.zip
	unzip $(IN_DIR)v001.00-connections.zip -d $(IN_DIR)

convert:
	mkdir -p $(OUT_DIR)
	./derivbaseru2useg.py <(cat <(tail -n +2 $(IN_DIR)connections_adj.csv) <(tail -n +2 $(IN_DIR)connections_adv.csv) <(tail -n +2 $(IN_DIR)connections_noun.csv) <(tail -n +2 $(IN_DIR)connections_rare.csv) <(tail -n +2 $(IN_DIR)connections_special_verb.csv) <(tail -n +2 $(IN_DIR)connections_verb.csv)) $(OUT_DIR)DerivBaseRU.useg > $(OUT_DIR)conversion.log

clean:
	rm -rf $(IN_DIR)
	rm -rf $(OUT_DIR)
