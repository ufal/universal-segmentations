.PHONY: download convert convert-en clean

DATADIR=../../data
IN_DIR=$(DATADIR)/original/MorphoLEX
OUT_DIR_eng=$(DATADIR)/converted/eng-MorphoLEX

PYTHONPATH=../../src
export PYTHONPATH

download: $(IN_DIR)/MorphoLEX_en.xlsx

$(IN_DIR)/MorphoLEX_en.xlsx: | $(IN_DIR)
	curl --location --compressed -o '$@' 'https://github.com/hugomailhot/MorphoLex-en/raw/master/MorphoLEX_en.xlsx'

$(IN_DIR):
	mkdir -p '$@'

$(OUT_DIR_eng):
	mkdir -p '$@'

convert: convert-eng

convert-eng: $(OUT_DIR_eng)/all.useg
# TODO Generate train / dev / test split.

$(OUT_DIR_eng)/all.useg: $(IN_DIR)/MorphoLEX_en.xlsx allomorphs-eng.tsv python-venv/bin/activate | $(OUT_DIR_eng)
	. python-venv/bin/activate && ./import_morpholex.py --annot-name '$(basename $(notdir $<))' --allomorphs allomorphs-eng.tsv '$<' > '$@' 2> '$(basename $@).log'

python-venv/bin/activate: requirements.txt
	rm -rf python-venv
	virtualenv -p python3 python-venv/
	. python-venv/bin/activate && pip install -r '$<'

clean:
	rm -rf '$(OUT_DIR_eng)'
	#rm -rf python-venv
	#rm -rf '$(IN_DIR)'
