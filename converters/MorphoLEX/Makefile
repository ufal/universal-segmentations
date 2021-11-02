.PHONY: download convert

DATADIR=../../data
IN_DIR=$(DATADIR)/original/MorphoLEX
OUT_DIR=$(DATADIR)/converted/en-MorphoLEX

PYTHONPATH=../../src
export PYTHONPATH

download: $(IN_DIR)/MorphoLEX_en.xlsx

$(IN_DIR)/MorphoLEX_en.xlsx: | $(IN_DIR)
	curl --location --compressed -o '$@' 'https://github.com/hugomailhot/MorphoLex-en/raw/master/MorphoLEX_en.xlsx'

$(IN_DIR):
	mkdir -p '$@'

$(OUT_DIR):
	mkdir -p '$@'

convert: $(OUT_DIR)/all.useg
# TODO Generate train / dev / test split.

$(OUT_DIR)/all.useg: $(IN_DIR)/MorphoLEX_en.xlsx python-venv/bin/activate | $(OUT_DIR)
	. python-venv/bin/activate && ./import_morpholex.py --annot-name '$(basename $(notdir $<))' --allomorphs allomorphs.tsv '$<' > '$@' 2> '$(basename $@).log'

python-venv/bin/activate: requirements.txt
	rm -rf python-venv
	virtualenv -p python3 python-venv/
	. python-venv/bin/activate && pip install -r '$<'
