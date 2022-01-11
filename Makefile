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

stats-%.tex: src/stats.py rewrite-names.sed
	cd data/converted && find * -name '*.useg' '!' '(' -path '*-UniMorph*' -o -path '*frc-*' -o -path '*RetrogradeDictionary*' -o -path '*ces-SlavickovaDict*' ')' -exec $(abspath src/stats.py) --printer tex --threads 8 --only '$*' '{}' '+' | sed -f '$(abspath rewrite-names.sed)' > '$(abspath $@)'

stats.tex: src/stats.py
	cd data/converted && $(abspath src/stats.py) --printer tex --threads 8 */*.useg > $(abspath $@)

stats-non-unimorph.tex: src/stats.py
	cd data/converted && find * -name '*.useg' -not -path '*UniMorph*' -exec $(abspath src/stats.py) --printer tex --threads 8 '{}' '+' > $(abspath $@)

poses.txt:
	find data/converted -name '*.useg' -exec cut -f3 '{}' '+' | sort -u > '$@'

pos-examples: poses.txt
	while IFS= read -r pos; do \
		printf '\n%s:\n' "$${pos}" && \
		for f in `find data/converted -name '*.useg'`; do \
			cut -f3 "$${f}" | fgrep -xqe "$${pos}" && printf '	%s\n' "$${f}"; \
		done; \
	done < '$<'

check-annot-names:
	for f in `find data/converted -name '*.useg'`; do \
		annot_names=`cut -f5 "$${f}" | grep -o '"annot_name": "[^"]*"' | sort -u`; \
		if [ -z "$${annot_names}" ]; then \
			printf 'NONE %s\n' "$${f}"; \
		elif [ "`printf '%s\n' "$${annot_names}" | wc -l`" -eq 1 ]; then \
			printf 'OK %s: %s\n' "$${f}" "$${annot_names}"; \
		else \
			printf 'ERR %s: %s\n' "$${f}" "$${annot_names}"; \
		fi; \
	done

clean:
	rm -f README.xhtml
	rm -f .coverage htmlcov/index.html
	rm -f stats.tex stats-non-unimorph.tex



convert-all:
	for convertor in $$(ls -1 converters/); do \
		cd converters/$$convertor/ ;\
		$(MAKE) download ;\
		$(MAKE) convert ;\
		cd .. ;\
	done


PUBLIC_DIR=data/release/UniSegments-1.0-public/data
PUBLIC_DIR_DOC=data/release/UniSegments-1.0-public/doc
PRIVATE_DIR=data/release/UniSegments-1.0-private/data
LICENCE_DIR=doc/licenses
prepare-release:
	rm -rf '$(PUBLIC_DIR)'
	rm -rf '$(PRIVATE_DIR)'
	mkdir -p data/release
	mkdir -p '$(PUBLIC_DIR)'
	mkdir -p '$(PRIVATE_DIR)'
	echo PRIVATE DATASETS:; \
	for data_directory in data/converted/*-CELEX; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/;\
	done; \
	for data_directory in data/converted/*-KuznetsEfremDict; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/;\
	done; \
	for data_directory in data/converted/*-KCIS; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/;\
	done; \
	for data_directory in data/converted/*-TichonovDict; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/;\
	done; \
	for data_directory in data/converted/*-SlavickovaDict; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/;\
	done; \
	for data_directory in data/converted/*-UniMorph; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-sa-3-0.txt $(PRIVATE_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-MorphoLex; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/;\
	done; \
	echo PUBLIC DATASETS:; \
	for data_directory in data/converted/*-DeriNet; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-nc-sa-3-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-CroDeriV; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-sa-3-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-Demonette; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-nc-sa-3-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-DerIvaTario; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-sa-4-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-DerivBaseDE; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-sa-3-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-DerivBaseRU; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/apache-2-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-Echantinom; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-4-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-MorphoChallenge; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r LICENCE $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-MorphyNet; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-sa-3-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-PersianMorphSegLex; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-nc-sa-4-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-Uniparser; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/mit.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/license.txt;\
	done; \
	for data_directory in data/converted/*-WordFormationLatin; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-nc-sa-4-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/license.txt;\
	done;
	mkdir -p $(PUBLIC_DIR_DOC)
	cp doc/readmes/readme-1-0.txt $(PUBLIC_DIR_DOC)/README.md
	cp doc/lindat-clariah-cz/license-data.txt $(PUBLIC_DIR_DOC)/LICENSE
	wget https://ufal.mff.cuni.cz/techrep/tr69.pdf -O $(PUBLIC_DIR_DOC)/Towards-Universal-Segmentations-Survey-of-Existing-Morphosegmentation-Resources.pdf
