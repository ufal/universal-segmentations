DATADIR=../../data/
IN_DIR=$(DATADIR)/original/WordFormationLatin/
OUT_DIR=$(DATADIR)/converted/lat-WordFormationLatin/

SHELL = bash


download:
	mkdir -p $(IN_DIR)
	cd $(IN_DIR) && curl -O https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3247/{UDer-1.1.tgz} && gzip -d UDer-1.1.tgz && tar xvf UDer-1.1.tar && cp UDer-1.1/la-WFL/UDer-1.1-la-WFL.tsv.gz . && gzip -d UDer-1.1-la-WFL.tsv.gz && rm UDer-1.1.tar && rm -r UDer-1.1

convert:
	echo $(IN_DIR)
	mkdir -p $(OUT_DIR)
	./converter_WFL.py < $(IN_DIR)/UDer-1.1-la-WFL.tsv > $(OUT_DIR)/UDer-1.1-la-WFL.useg

