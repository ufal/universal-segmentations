.PHONY: all lint profile clean
.SECONDARY:

DERINET_API_DIR:=./derinet2
UDER_DIR:=./UDer-1.1

all: udm/udmurt.useg ces/czech.useg deu/german.useg eng/english.useg

eng/MorphoLEX_en.xlsx: | eng
	curl --location --compressed -o '$@' 'https://github.com/hugomailhot/MorphoLex-en/raw/master/MorphoLEX_en.xlsx'

fra/MorphoLEX_fr.xlsx: | fra
	curl --location --compressed -o '$@' 'https://github.com/hugomailhot/morpholex-fr/raw/master/xlsx/Morpholex_FR.xlsx'

udm/udmurt.useg: udm/wordlist_analyzed_fixed.txt src/import_udmurt.py src/useg/seg_lex.py src/useg/seg_tsv.py
	./src/import_udmurt.py < '$<' 2>&1 > '$@' | tee '$(basename $@).log' >&2

udm/wordlist_analyzed_fixed.txt: udm/wordlist_analyzed.txt
	# There are some spurious underscores in some word forms;
	#  get rid of them. Also, fix STEMSTEM -> STEM
	sed -e 's/__//; s/_</</; s/"STEMSTEM"/"STEM"/' < '$<' > '$@'

udm/wordlist_analyzed.txt: | udm
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-udm/raw/master/wordlists/wordlist_analyzed.txt'

udm:
	mkdir -p '$@'
ces:
	mkdir -p '$@'
deu:
	mkdir -p '$@'
eng:
	mkdir -p '$@'
fra:
	mkdir -p '$@'

ces/czech.useg: $(UDER_DIR)/cs-DeriNet/UDer-1.1-cs-DeriNet.tsv | $(DERINET_API_DIR) ces
	PYTHONPATH='$(DERINET_API_DIR)' ./src/import_derinet.py --annot-name "DeriNet 2.1" < '$<' > '$@'

deu/german.useg: $(UDER_DIR)/de-GCelex/UDer-1.1-de-GCelex.tsv | $(DERINET_API_DIR) deu
	PYTHONPATH='$(DERINET_API_DIR)' ./src/import_derinet.py --annot-name "GCelex" < '$<' > '$@'

eng/english.useg: eng/MorphoLEX_en.xlsx src/import_morpholex.py | eng
	./src/import_morpholex.py --annot-name '$(basename $<)' '$<' > '$@' 2> '$(basename $@).log'

$(DERINET_API_DIR):
	@printf 'Please, point the DERINET_API_DIR variable at a directory with the DeriNet 2.0 Python API. Current value "%s" is not valid.\n' '$(DERINET_API_DIR)' >&2; exit 1

lint:
	pylint src/

profile: udm/wordlist_analyzed_fixed.txt src/import_udmurt.py src/useg/seg_lex.py src/useg/seg_tsv.py
# 	python3 -m scalene --cpu-only --outfile '$@' src/import_udmurt.py < '$<' > /dev/null
	python3 -m cProfile --outfile '$@' src/import_udmurt.py < '$<' > /dev/null
	snakeviz '$@'

README.xhtml: README.adoc
	asciidoc --backend=xhtml11 -o '$@' '$<'

clean:
	rm -f udm/wordlist_analyzed_fixed.txt
	rm -f udm/udmurt.useg udm/udmurt.log
	#rm -f udm/wordlist_analyzed.txt
	#rm -f eng/MorphoLEX_en.xlsx
	rm -f eng/english.useg eng/english.log
	#rm -f fra/MorphoLEX_fr.xlsx
	rm -f README.xhtml
