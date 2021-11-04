.PHONY: download convert

DATADIR=../../data
IN_DIR=$(DATADIR)/original/UDer-1.1
OUT_DIR=$(DATADIR)/converted/ces-DeriNet

DERINET_API_DIR:=../../derinet2

PYTHONPATH=../../src:$(DERINET_API_DIR)
export PYTHONPATH

download: $(IN_DIR)/cs-DeriNet/UDer-1.1-cs-DeriNet.tsv

$(IN_DIR)/cs-DeriNet/UDer-1.1-cs-DeriNet.tsv.gz: $(IN_DIR)/UDer-1.1.tgz
	tar -xvf '$<' --directory='$(IN_DIR)' --strip-components=1 --touch 'UDer-1.1/cs-DeriNet/UDer-1.1-cs-DeriNet.tsv.gz'

$(IN_DIR)/cs-DeriNet/UDer-1.1-cs-DeriNet.tsv: $(IN_DIR)/cs-DeriNet/UDer-1.1-cs-DeriNet.tsv.gz
	gzip -dkf '$<'

$(IN_DIR)/UDer-1.1.tgz: | $(IN_DIR)
	curl -o '$@' 'https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3247/UDer-1.1.tgz'

$(IN_DIR):
	mkdir -p '$@'

$(OUT_DIR):
	mkdir -p '$@'

$(DERINET_API_DIR):
	@printf 'Please, point the DERINET_API_DIR variable at a directory with the DeriNet 2.0 Python API. Current value "%s" is not valid.\n' '$(DERINET_API_DIR)' >&2; exit 1

convert: $(OUT_DIR)/all.useg
# TODO Generate train / dev / test split.

$(OUT_DIR)/all.useg: $(IN_DIR)/cs-DeriNet/UDer-1.1-cs-DeriNet.tsv | $(OUT_DIR)
	./import_derinet.py --annot-name 'DeriNet-2.1' < '$<' 2>&1 > '$@' | tee '$(basename $@).log' >&2
