DATADIR=../../data/
IN_DIR=$(DATADIR)/original/Demonette/
OUT_DIR=$(DATADIR)/converted/fr-Demonette/

SHELL = bash


download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	cd $(IN_DIR) && wget http://redac.univ-tlse2.fr/lexiques/demonette/demonette-1.2.zip && unzip demonette-1.2.zip
	#rsync -r $(IN_DIR)$ bafna@osiris.ms.mff.cuni.cz:/net/work/projects/universal-segmentations/data/original

convert:
	mkdir -p $(OUT_DIR)
	./fr_demonette2useg.py $(IN_DIR)/demonette-1.2.csv  $(OUT_DIR)$/with_duplicates.useg
#	wc -l $(OUT_DIR)$/with_duplicates.useg
	cat $(OUT_DIR)$/with_duplicates.useg | sort | uniq > $(OUT_DIR)$/fr_demonette.useg
#	wc -l $(OUT_DIR)$/fr_demonette.useg
	cat $(OUT_DIR)$/fr_demonette.useg | grep "derif" > $(OUT_DIR)$/fr_demonette.derif.useg
	cat $(OUT_DIR)$/fr_demonette.useg | grep "demonette" > $(OUT_DIR)$/fr_demonette.demonette.useg
	rm $(OUT_DIR)$/with_duplicates.useg
	rm $(OUT_DIR)$/fr_demonette.useg

