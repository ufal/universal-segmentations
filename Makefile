.PHONY: all lint profile test clean
.SECONDARY:

all: README.xhtml

lint:
	pylint src/

#profile: udm/wordlist_analyzed_fixed.txt src/import_udmurt.py src/useg/seg_lex.py src/useg/seg_tsv.py
## 	python3 -m scalene --cpu-only --outfile '$@' src/import_udmurt.py < '$<' > /dev/null
#	python3 -m cProfile --outfile '$@' src/import_udmurt.py < '$<' > /dev/null
#	snakeviz '$@'

test:
	PYTHONPATH=src/ nosetests -w test/

README.xhtml: README.adoc
	asciidoc --backend=xhtml11 -o '$@' '$<'

clean:
	rm -f README.xhtml
