DATADIR=../../data/
IN_DIR=$(DATADIR)/original/Demonette/
OUT_DIR=$(DATADIR)/converted/fra-Demonette/

SHELL = bash


download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	cd $(IN_DIR) && wget http://redac.univ-tlse2.fr/lexiques/demonette/demonette-1.2.zip && unzip demonette-1.2.zip
	#rsync -r $(IN_DIR)$ bafna@osiris.ms.mff.cuni.cz:/net/work/projects/universal-segmentations/data/original

convert:
	mkdir -p $(OUT_DIR)
	./fra_demonette2useg.py $(IN_DIR)/demonette-1.2.csv  $(OUT_DIR)$/with_duplicates.useg
#	wc -l $(OUT_DIR)$/with_duplicates.useg
	cat $(OUT_DIR)$/with_duplicates.useg | PYTHONPATH=../../src/ python3 ../../test/test_round_trip.py  | uniq > $(OUT_DIR)$/fra_demonette.useg
#	wc -l $(OUT_DIR)$/fra_demonette.useg
#	cat $(OUT_DIR)$/fra_demonette.useg | grep "derif" > $(OUT_DIR)$/fra_demonette.derif.useg
#	cat $(OUT_DIR)$/fra_demonette.useg | grep "demonette" > $(OUT_DIR)$/fra_demonette.demonette.useg
#	cat $(OUT_DIR)$/fra_demonette.useg | grep -v "demonette" | grep -v "derif" > $(OUT_DIR)$/fra_demonette.other.useg
	rm $(OUT_DIR)$/with_duplicates.useg
#	rm $(OUT_DIR)$/fra_demonette.useg
