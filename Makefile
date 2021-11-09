.PHONY: all lint profile test test-all clean
.SECONDARY:
.SUFFIXES:

all: README.xhtml

lint:
	pylint src/

#profile: udm/wordlist_analyzed_fixed.txt src/import_udmurt.py src/useg/seg_lex.py src/useg/seg_tsv.py
## 	python3 -m scalene --cpu-only --outfile '$@' src/import_udmurt.py < '$<' > /dev/null
#	python3 -m cProfile --outfile '$@' src/import_udmurt.py < '$<' > /dev/null
#	snakeviz '$@'

test:
	@if command -v pytest > /dev/null; then \
		PYTHONPATH=src/ pytest test/ ; \
	else \
		PYTHONPATH=src/ python -m unittest discover test/ ; \
	fi

test-all: data/converted/udm-Uniparser/all.useg test test/test_round_trip.sh test/test_round_trip.py
	./test/test_round_trip.sh '$<'

coverage: htmlcov/index.html
# 	xdg-open '$<'

htmlcov/index.html: .coverage
	coverage html

.coverage: $(wildcard test/*.py) $(wildcard src/useg/*.py)
	PYTHONPATH=src/ coverage run --branch -m pytest test/

README.xhtml: README.adoc
	asciidoc --backend=xhtml11 -o '$@' '$<'

stats.tex: src/stats.py
	cd data/converted && $(abspath src/stats.py) --printer tex --threads 8 */*.useg > $(abspath $@)

stats-non-unimorph.tex: src/stats.py
	cd data/converted && find . -name '*.useg' -not -path '*UniMorph*' -exec $(abspath src/stats.py) --printer tex --threads 8 '{}' '+' > $(abspath $@)

clean:
	rm -f README.xhtml
	rm -f .coverage htmlcov/index.html
	rm -f stats.tex stats-non-unimorph.tex
