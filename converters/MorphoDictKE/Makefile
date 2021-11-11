DATADIR=../../data/
IN_DIR=$(DATADIR)/original/MorphoDictKE/
OUT_DIR=$(DATADIR)/converted/rus-MorphoDictKE/

SHELL = bash


download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	cd $(IN_DIR) && wget https://raw.githubusercontent.com/olesar/Reproducible-Research/master/ruWordFormation/morphodictKE1985.txt

convert:
	mkdir -p $(OUT_DIR)
	./morphodict2useg.py $(IN_DIR)morphodictKE1985.txt $(OUT_DIR)MorphoDictKE.useg

clean:
	rm -rf $(IN_DIR)
	rm -rf $(OUT_DIR)
