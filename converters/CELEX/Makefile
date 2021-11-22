.PHONY: download convert

DATADIR:=../../data
IN_DIR:=$(DATADIR)/original/CELEX
OUT_DIR_deu:=$(DATADIR)/converted/deu-CELEX
OUT_DIR_eng:=$(DATADIR)/converted/eng-CELEX
OUT_DIR_nld:=$(DATADIR)/converted/nld-CELEX

PYTHONPATH:=$(abspath ../../src):$(abspath ../../derinet2)
export PYTHONPATH

download: $(IN_DIR)/UDer-1.1-de-GCelex-nomorphs.tsv $(IN_DIR)/UDer-1.1-en-ECelex.tsv $(IN_DIR)/UDer-1.1-nl-DCelex.tsv

# The dependency is not recorded, so that the recipe works outside of
#  the UFAL network if you supply the data manually.
$(IN_DIR)/UDer-1.1-de-GCelex-nomorphs.tsv: | $(IN_DIR)
	cp /net/work/people/vidra/universal-derivations/de/GCelex/UDer-1.1-de-GCelex-nomorphs.tsv '$@'
$(IN_DIR)/UDer-1.1-en-ECelex.tsv: | $(IN_DIR)
	cp /net/work/people/vidra/universal-derivations/en/ECelex/UDer-1.1-en-ECelex.tsv '$@'
$(IN_DIR)/UDer-1.1-nl-DCelex.tsv: | $(IN_DIR)
	cp /net/work/people/vidra/universal-derivations/nl/DCelex/UDer-1.1-nl-DCelex.tsv '$@'

$(IN_DIR):
	mkdir -p '$@'

$(OUT_DIR_deu):
	mkdir -p '$@'
$(OUT_DIR_eng):
	mkdir -p '$@'
$(OUT_DIR_nld):
	mkdir -p '$@'

convert: $(OUT_DIR_deu)/all.useg $(OUT_DIR_eng)/all.useg $(OUT_DIR_nld)/all.useg
# TODO Generate train / dev / test split.

$(OUT_DIR_deu)/all.useg: $(IN_DIR)/UDer-1.1-de-GCelex-nomorphs.tsv import_celex.py | $(OUT_DIR_deu)
	./import_celex.py --lang deu < '$<' > '$@' 2> '$(basename $@).log'

$(OUT_DIR_eng)/all.useg: $(IN_DIR)/UDer-1.1-en-ECelex.tsv import_celex.py | $(OUT_DIR_eng)
	./import_celex.py --lang eng < '$<' > '$@' 2> '$(basename $@).log'

$(OUT_DIR_nld)/all.useg: $(IN_DIR)/UDer-1.1-nl-DCelex.tsv import_celex.py | $(OUT_DIR_nld)
	./import_celex.py --lang nld < '$<' > '$@' 2> '$(basename $@).log'
