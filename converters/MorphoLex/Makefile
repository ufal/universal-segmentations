.PHONY: download convert convert-en convert-fr clean

DATADIR=../../data
IN_DIR=$(DATADIR)/original/MorphoLex
OUT_DIR_eng=$(DATADIR)/converted/eng-MorphoLex
OUT_DIR_fra=$(DATADIR)/converted/fra-MorphoLex

PYTHONPATH=../../src
export PYTHONPATH

download: $(IN_DIR)/MorphoLex_en.xlsx $(IN_DIR)/MorphoLex_fr.xlsx

$(IN_DIR)/MorphoLex_en.xlsx: | $(IN_DIR)
	curl --location --compressed -o '$@' 'https://github.com/hugomailhot/MorphoLex-en/raw/master/MorphoLEX_en.xlsx'

$(IN_DIR)/MorphoLex_fr.xlsx: | $(IN_DIR)
	curl --location --compressed -o '$@' 'https://github.com/hugomailhot/morpholex-fr/raw/master/xlsx/Morpholex_FR.xlsx'

$(IN_DIR):
	mkdir -p '$@'

$(OUT_DIR_eng):
	mkdir -p '$@'

$(OUT_DIR_fra):
	mkdir -p '$@'

convert: convert-eng convert-fra

convert-eng: $(OUT_DIR_eng)/all.useg
convert-fra: $(OUT_DIR_fra)/all.useg
# TODO Generate train / dev / test split.

$(OUT_DIR_eng)/all.useg: $(IN_DIR)/MorphoLex_en.xlsx allomorphs-eng.tsv python-venv/bin/activate | $(OUT_DIR_eng)
	. python-venv/bin/activate && ./import_morpholex.py --annot-name '$(basename $(notdir $<))' --allomorphs allomorphs-eng.tsv '$<' > '$@' 2> '$(basename $@).log'

$(OUT_DIR_fra)/all.useg: $(IN_DIR)/MorphoLex_fr.xlsx allomorphs-fra.tsv python-venv/bin/activate | $(OUT_DIR_fra)
	. python-venv/bin/activate && ./import_morpholex.py --annot-name '$(basename $(notdir $<))' --allomorphs allomorphs-fra.tsv '$<' > '$@' 2> '$(basename $@).log'

python-venv/bin/activate: requirements.txt
	rm -rf python-venv
	virtualenv -p python3 python-venv/
	. python-venv/bin/activate && pip install -r '$<'

clean:
	rm -rf '$(OUT_DIR_eng)' '$(OUT_DIR_fra)'
	#rm -rf python-venv
	#rm -rf '$(IN_DIR)'
