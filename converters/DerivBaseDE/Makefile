DATADIR=../../data/
IN_DIR=$(DATADIR)/original/DerivBaseDE/
OUT_DIR=$(DATADIR)/converted/deu-DerivBaseDE/

SHELL = bash


download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	cd $(IN_DIR) && wget https://www.ims.uni-stuttgart.de/documents/ressourcen/lexika/derivbase/derivbase-v2.0.zip
	unzip $(IN_DIR)derivbase-v2.0.zip -d $(IN_DIR)

convert:
	mkdir -p $(OUT_DIR)
	# for file in $(IN_DIR)connections_adj.csv $(IN_DIR)connections_adv.csv $(IN_DIR)connections_noun.csv $(IN_DIR)connections_rare.csv $(IN_DIR)connections_special_verb.csv $(IN_DIR)connections_verb.csv ; do \
	# 	./derivbaseru2useg.py $${file} $(OUT_DIR)$${file}.useg;\
	# done
