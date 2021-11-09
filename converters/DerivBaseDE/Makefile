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
	./derivbasede2useg.py $(IN_DIR)/derivbase/DErivBase-v2.0-rulePaths.txt $(IN_DIR)/derivbase/DErivBase-v1.4.1-rules.txt $(OUT_DIR)DErivBaseDE.useg
