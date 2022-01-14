DATADIR=../../data
IN_DIR=$(DATADIR)/original/MorphoChallenge
OUT_DIR=$(DATADIR)/converted

SHELL = bash


download: # and unpack, if needed
	mkdir -p $(IN_DIR)
	for lang in eng fin tur; do \
		wget http://morpho.aalto.fi/events/morphochallenge2010/data/goldstd_combined.segmentation."$$lang" -O $(IN_DIR)/both_2010_"$$lang".txt; \
	done
	wget http://morpho.aalto.fi/events/morphochallenge2010/data/goldstd_combined.labels.ger -O $(IN_DIR)/morphemes_2010_ger.txt

	for lang in eng fin tur ger; do \
		for year in 2007 2008 2009; do \
			wget http://morpho.aalto.fi/events/morphochallenge"$$year"/data/goldstdsample."$$lang" -O $(IN_DIR)/morphemes_"$$year"_"$$lang".txt; \
		done; \
		cat $(IN_DIR)/morphemes_*_"$$lang".txt | sort -u > $(IN_DIR)/morphemes_all_"$$lang".txt; \
	done

	for lang in eng fin tur; do \
		wget http://morpho.aalto.fi/events/morphochallenge2005/data/goldstdsample."$$lang" -O $(IN_DIR)/morphs_2005_"$$lang".txt; \
	done


convert:
	for lang in eng fin tur deu; do \
		mkdir -p $(OUT_DIR)/"$$lang"-MorphoChallenge/;\
		mkdir -p $(OUT_DIR)/"$$lang"-MorphoChallenge/logs;\
	done

	python ./convert_morphemes.py $(IN_DIR)/morphemes_all_eng.txt $(IN_DIR)/both_2010_eng.txt $(OUT_DIR)/eng-MorphoChallenge/MorphoChallenge_eng.useg 2>/dev/stdout | tee $(OUT_DIR)/eng-MorphoChallenge/logs/07080910_eng_log.txt
	python ./convert_morphemes.py $(IN_DIR)/morphemes_all_fin.txt $(IN_DIR)/both_2010_fin.txt $(OUT_DIR)/fin-MorphoChallenge/MorphoChallenge_fin.useg 2>/dev/stdout | tee $(OUT_DIR)/fin-MorphoChallenge/logs/07080910_fin_log.txt
	python ./convert_morphemes.py $(IN_DIR)/morphemes_all_tur.txt $(IN_DIR)/both_2010_tur.txt $(OUT_DIR)/tur-MorphoChallenge/MorphoChallenge_tur.useg 2>/dev/stdout | tee $(OUT_DIR)/tur-MorphoChallenge/logs/07080910_tur_log.txt

	python ./convert_morphemes.py $(IN_DIR)/morphemes_all_ger.txt "" $(OUT_DIR)/deu-MorphoChallenge/MorphoChallenge_deu.useg 2>/dev/stdout | tee $(OUT_DIR)/deu-MorphoChallenge/logs/07080910_deu_log.txt

	for lang in eng fin tur; do \
		python ./convert_morphs.py $(IN_DIR)/morphs_2005_"$$lang".txt $(OUT_DIR)/"$$lang"-MorphoChallenge/MorphoChallenge05_"$$lang".useg 2>/dev/stdout | tee $(OUT_DIR)/"$$lang"-MorphoChallenge/logs/05_"$$lang"_log.txt; \
		cat $(OUT_DIR)/"$$lang"-MorphoChallenge/MorphoChallenge05_"$$lang".useg $(OUT_DIR)/"$$lang"-MorphoChallenge/MorphoChallenge_"$$lang".useg | sort -u > $(OUT_DIR)/"$$lang"-MorphoChallenge/MorphoChallenge_"$$lang"_.useg;\
		rm $(OUT_DIR)/"$$lang"-MorphoChallenge/MorphoChallenge05_"$$lang".useg; \
		PYTHONPATH=../../src python ./do_round_trip.py $(OUT_DIR)/"$$lang"-MorphoChallenge/MorphoChallenge_"$$lang"_.useg $(OUT_DIR)/"$$lang"-MorphoChallenge/MorphoChallenge_"$$lang".useg ;\
	done
