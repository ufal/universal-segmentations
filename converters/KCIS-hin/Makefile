DATADIR=../../data/
IN_DIR=$(DATADIR)/original/KCIS/hin/
OUT_DIR=$(DATADIR)/converted/hin-KCIS/

SHELL = bash


download: # and unpack, if needed
	echo "Already downloaded!"
	cat $(IN_DIR)/*/Data/* > $(IN_DIR)/aggregated.txt

convert:
	mkdir -p $(OUT_DIR)
	cat $(IN_DIR)/aggregated.txt | cut -f2- | grep fs | grep -v "((\|PUNC" |  sort | uniq > $(IN_DIR)/simplified_ssf.txt

	./hin_kcis2useg.py $(IN_DIR)/simplified_ssf.txt  $(OUT_DIR)$/with_duplicates.useg

	cat $(OUT_DIR)$/with_duplicates.useg | uniq > $(OUT_DIR)$/hin_kcis.useg
	rm $(OUT_DIR)$/with_duplicates.useg
	rm $(IN_DIR)/simplified_ssf.txt
