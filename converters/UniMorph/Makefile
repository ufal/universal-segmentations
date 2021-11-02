DATADIR=../../data/
TMPDIR=./tmp
IN_DIR= $(DATADIR)/original/UniMorph/

SHELL = bash

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir := $(dir $(mkfile_path))

download:
	mkdir -p $(IN_DIR)
	mkdir  -p $(TMPDIR)
	cd $(TMPDIR) && wget https://unimorph.github.io/
	less tmp/index.html | perl -ne 'print "$$1\n" if /"(https:\/\/github.com\/unimorph\/...)"/' > tmp/git.urls

	cd $(IN_DIR) && for f in `cat $(mkfile_dir)/tmp/git.urls`; do  git clone $$f ; done
