DATADIR=../../data/
IN_DIR=$(DATADIR)/original/KCIS/mar/
OUT_DIR=$(DATADIR)/converted/mar-KCIS/

SHELL = bash


download: # and unpack, if needed
	echo "TODO!!"

convert:
	mkdir -p $(OUT_DIR)
	cat $(IN_DIR)/Data/Development/General/Marathi_Dependency_Tree_41.txt | cut -f2- | grep fs | grep -v "((\|PUNC" |  sort | uniq > $(IN_DIR)/Data/Development/General/simplified_ssf.txt
	
	./mar_kcis2useg.py $(IN_DIR)/Data/Development/General/simplified_ssf.txt  $(OUT_DIR)$/with_duplicates.useg

	cat $(OUT_DIR)$/with_duplicates.useg | sort | uniq > $(OUT_DIR)$/mar_kcis.useg
	rm $(OUT_DIR)$/with_duplicates.useg
	rm $(IN_DIR)/Data/Development/General/simplified_ssf.txt
