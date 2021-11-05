.PHONY: download convert

DATADIR:=../../data
IN_DIR:=$(DATADIR)/original/CELEX
OUT_DIR:=$(DATADIR)/converted/deu-CELEX

PYTHONPATH:=$(abspath ../../src):$(abspath ../../derinet2)
export PYTHONPATH

download: $(IN_DIR)/UDer-1.1-de-GCelex-nomorphs.tsv | $(IN_DIR)

# The dependency is not recorded, so that the recipe works outside of
#  the UFAL network if you supply the data manually.
$(IN_DIR)/UDer-1.1-de-GCelex-nomorphs.tsv:
	cp /net/work/people/vidra/universal-derivations/de/GCelex/UDer-1.1-de-GCelex-nomorphs.tsv '$@'

$(IN_DIR):
	mkdir -p '$@'

$(OUT_DIR):
	mkdir -p '$@'

convert: $(OUT_DIR)/all.useg
# TODO Generate train / dev / test split.

$(OUT_DIR)/all.useg: $(IN_DIR)/UDer-1.1-de-GCelex-nomorphs.tsv import_decelex.py | $(OUT_DIR)
	./import_decelex.py < '$<' > '$@' 2> '$(basename $@).log'
