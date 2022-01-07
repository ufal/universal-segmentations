.PHONY: all lint profile test test-all stats clean
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

stats: stats-left.tex stats-right.tex

stats-%.tex: src/stats.py
	cd data/converted && find * -name '*.useg' '!' '(' -path '*-UniMorph*' -o -path '*frc-*' -o -path '*RetrogradeDictionary*' ')' -exec $(abspath src/stats.py) --printer tex --threads 8 --only '$*' '{}' '+' > $(abspath $@)

stats.tex: src/stats.py
	cd data/converted && $(abspath src/stats.py) --printer tex --threads 8 */*.useg > $(abspath $@)

stats-non-unimorph.tex: src/stats.py
	cd data/converted && find * -name '*.useg' -not -path '*UniMorph*' -exec $(abspath src/stats.py) --printer tex --threads 8 '{}' '+' > $(abspath $@)

clean:
	rm -f README.xhtml
	rm -f .coverage htmlcov/index.html
	rm -f stats.tex stats-non-unimorph.tex





PUBLIC_DIR=data/release/UniSegs-0.1-public/data
PRIVATE_DIR=data/release/UniSegs-0.1-private/data
prepare-release:
	rm -rf data/release
	mkdir data/release
	mkdir -p $(PUBLIC_DIR)
	mkdir -p $(PRIVATE_DIR)
	for data_directory in data/converted/*-CELEX; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PRIVATE_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-MorphoDictKE; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PRIVATE_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-KCIS; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PRIVATE_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-Tikhonov; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PRIVATE_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-RetrogradeDictionary; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PRIVATE_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-UniMorph; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PRIVATE_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-DeriNet; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-CroDeriV; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-Demonette; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-DerIvaTario; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-DerivBaseDE; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-DerivBaseRU; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-Echantinom; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-MorphoChallenge; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-MorphoLex; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-MorphyNet; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-PersianMorphSegLex; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-Uniparser; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-WordFormationLatin; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')";\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$(data_directory) | sed -r 's-.*/--')"/license.txt;\
	done;
