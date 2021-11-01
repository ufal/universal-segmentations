DATADIR=../../data/
IN_DIR=$(DATADIR)/original/FrenchDemonette/
OUT_DIR=$(DATADIR)/converted/fr-FrenchDemonette/

SHELL = bash


download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	cd $(IN_DIR) && wget http://redac.univ-tlse2.fr/lexiques/demonette/demonette-1.2.zip && unzip demonette-1.2.zip

convert:
	mkdir -p $(OUT_DIR)
	./fr_demonette2useg.py $(IN_DIR)/demonette-1.2.csv  $(OUT_DIR)$/fr_demonette.useg

