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
	@if python3 -m pytest --version > /dev/null 2>&1; then \
		PYTHONPATH=src/ python3 -m pytest test/ ; \
	else \
		PYTHONPATH=src/ python3 -m unittest discover test/ ; \
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
	find data/converted -name '*.useg' -exec cut -f3 '{}' '+' | grep -Fxve 'ADJ' -e 'ADP' -e 'ADV' -e 'AUX' -e 'CCONJ' -e 'DET' -e 'INTJ' -e 'NOUN' -e 'NUM' -e 'PART' -e 'PRON' -e 'PROPN' -e 'PUNCT' -e 'SCONJ' -e 'SYM' -e 'VERB' -e 'X' -e '' -e 'SCONJ|CCONJ' | sort -u > '$@'

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


doc/licenses/Uniparser/aii.txt: | doc/licenses/Uniparser
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-urmi/raw/master/LICENSE'
doc/licenses/Uniparser/hye.txt: | doc/licenses/Uniparser
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-eastern-armenian/raw/master/LICENSE'
doc/licenses/Uniparser/kpv.txt: | doc/licenses/Uniparser
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-komi-zyrian/raw/master/LICENSE'
doc/licenses/Uniparser/mdf.txt: | doc/licenses/Uniparser
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-moksha/raw/master/LICENSE'
doc/licenses/Uniparser/mhr.txt: | doc/licenses/Uniparser
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-meadow-mari/raw/master/LICENSE'
doc/licenses/Uniparser/myv.txt: | doc/licenses/Uniparser
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-erzya/raw/master/LICENSE'
doc/licenses/Uniparser/sqi.txt: | doc/licenses/Uniparser
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-albanian/raw/master/LICENSE'
doc/licenses/Uniparser/tgk.txt: | doc/licenses/Uniparser
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-tajik/raw/master/LICENSE.md'
doc/licenses/Uniparser/tru.txt: | doc/licenses/Uniparser
	curl --location --compressed -o '$@' 'https://github.com/margisk/uniparser-grammar-turoyo/raw/master/LICENSE'
doc/licenses/Uniparser/udm.txt: | doc/licenses/Uniparser
	curl --location --compressed -o '$@' 'https://github.com/timarkh/uniparser-grammar-udm/raw/master/LICENSE'
doc/licenses/Uniparser:
	mkdir -p '$@'
doc/licenses/Uniparser/.all: doc/licenses/Uniparser/aii.txt doc/licenses/Uniparser/hye.txt doc/licenses/Uniparser/kpv.txt doc/licenses/Uniparser/mdf.txt doc/licenses/Uniparser/mhr.txt doc/licenses/Uniparser/myv.txt doc/licenses/Uniparser/sqi.txt doc/licenses/Uniparser/tgk.txt doc/licenses/Uniparser/tru.txt doc/licenses/Uniparser/udm.txt
	touch '$@'


convert-all:
	for convertor in $$(ls -1 converters/); do \
		cd converters/$$convertor/ ;\
		$(MAKE) download ;\
		$(MAKE) convert ;\
		cd .. ;\
	done


RELEASE_DIR=data/release
PUBLIC_DIR=$(RELEASE_DIR)/UniSegments-1.0-public/data
PUBLIC_DIR_DOC=$(RELEASE_DIR)/UniSegments-1.0-public/doc
PRIVATE_DIR=$(RELEASE_DIR)/UniSegments-1.0-private/data
LICENCE_DIR=doc/licenses
prepare-release: doc/licenses/Uniparser/.all
	rm -rf '$(PUBLIC_DIR)'
	rm -rf '$(PRIVATE_DIR)'
	mkdir -p '$(RELEASE_DIR)'
	mkdir -p '$(PUBLIC_DIR)'
	mkdir -p '$(PRIVATE_DIR)'
	set -e; \
	echo PRIVATE DATASETS:; \
	for data_directory in data/converted/*-MorphoChallenge; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/;\
	done; \
	for data_directory in data/converted/*-CELEX; do \
		cp -r "$$data_directory" $(PRIVATE_DIR)/;\
	done; \
	for data_directory in data/converted/*-KuznetsEfremDict; do \
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
		cp -r $(LICENCE_DIR)/cc-by-sa-3-0.txt $(PRIVATE_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done; \
	echo PUBLIC DATASETS:; \
	for data_directory in data/converted/*-KCIS; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-nc-4-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done; \
	for data_directory in data/converted/*-DeriNet; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-nc-sa-3-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done; \
	for data_directory in data/converted/*-CroDeriV; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-sa-3-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done; \
	for data_directory in data/converted/*-Demonette; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-nc-sa-3-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done; \
	for data_directory in data/converted/*-DerIvaTario; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-sa-4-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done; \
	for data_directory in data/converted/*-DerivBaseDE; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-sa-3-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done; \
	for data_directory in data/converted/*-DerivBaseRU; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/apache-2-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done; \
	for data_directory in data/converted/*-Echantinom; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-4-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done; \
	for data_directory in data/converted/*-MorphoLex; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-nc-sa-4-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done; \
	for data_directory in data/converted/*-MorphyNet; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-sa-3-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done; \
	for data_directory in data/converted/*-PerSegLex; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-nc-sa-4-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done; \
	for data_directory in data/converted/*-Uniparser; do \
		lang_iso=`printf '%s' "$${data_directory}" | sed -e 'sX.*/XX; sX-.*XX'`;\
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp '$(LICENCE_DIR)'/Uniparser/"$${lang_iso}.txt" $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done; \
	for data_directory in data/converted/*-WordFormationLatin; do \
		cp -r "$$data_directory" $(PUBLIC_DIR)/;\
		cp -r $(LICENCE_DIR)/cc-by-nc-sa-4-0.txt $(PUBLIC_DIR)/"$$(echo $$data_directory | sed -r 's-.*/--')"/LICENSE.TXT;\
	done;
	#cleanup:
	echo deleting:
	find $(PUBLIC_DIR) $(PRIVATE_DIR) -type f ! -name LICENSE.TXT ! -name *.useg -delete
	find $(PUBLIC_DIR) $(PRIVATE_DIR) -type d -empty -delete
	for data_directory in $(PUBLIC_DIR)/* $(PRIVATE_DIR)/*; do \
		for useg_file in $$data_directory/*.useg; do\
			mv -n $$useg_file $$data_directory/UniSegments-1.0-$$(echo $$data_directory | sed -r 's-.*/--').useg;\
		done;\
	done; \
	mkdir -p $(PUBLIC_DIR_DOC)
	cp doc/readmes/readme-1-0.txt $(PUBLIC_DIR_DOC)/README.md
	cp doc/lindat-clariah-cz/license-data.txt $(PUBLIC_DIR_DOC)/LICENSE
	wget https://ufal.mff.cuni.cz/techrep/tr69.pdf -O $(PUBLIC_DIR_DOC)/Towards-Universal-Segmentations-Survey-of-Existing-Morphosegmentation-Resources.pdf
