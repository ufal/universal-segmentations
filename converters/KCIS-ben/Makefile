DATADIR=../../data/
IN_DIR=$(DATADIR)/original/KCIS/ben/
OUT_DIR=$(DATADIR)/converted/ben-KCIS/

SHELL = bash


download: # and unpack, if needed
	echo "Already downloaded!"
	cat $(IN_DIR)/Data/*/* > $(IN_DIR)/aggregated.txt

convert:
	mkdir -p $(OUT_DIR)
	cat $(IN_DIR)/aggregated.txt | cut -f2- | grep fs | grep -v "((\|PUNC" |  sort | uniq > $(IN_DIR)/simplified_ssf.txt

	./ben_kcis2useg.py $(IN_DIR)/simplified_ssf.txt  $(OUT_DIR)$/with_duplicates.useg

	cat $(OUT_DIR)$/with_duplicates.useg | PYTHONPATH=../../src/ python3 ../../test/test_round_trip.py | uniq > $(OUT_DIR)$/ben_kcis.useg
	rm $(OUT_DIR)$/with_duplicates.useg
	rm $(IN_DIR)/simplified_ssf.txt
