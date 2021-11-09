DATADIR=../../data/
IN_DIR=$(DATADIR)/original/DerIvaTario/
OUT_DIR=$(DATADIR)/converted/ita-DerIvaTario/

SHELL = bash


download: # and unpack, if needed
	echo "Can't be downloaded at the moment!"
	
convert:
	mkdir -p $(OUT_DIR)
	./ita_derivatario2useg.py $(IN_DIR)/derivatario.csv $(IN_DIR)/UDer-1.1-it-DerIvaTario.tsv $(OUT_DIR)$/ita-derivatario.useg
