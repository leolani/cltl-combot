SHELL=/bin/bash

$(info Project $(project_name), version: $(project_version), in $(project_root))

.DEFAULT_GOAL := install

# Implicit rules
.PHONY: depend
depend:

.PHONY: clean
clean: base-clean

.PHONY: touch-version
touch-version:

.PHONY: version
version: version.txt

version.txt: $(addsuffix /version.txt, $(dependencies))

.PHONY: version
build: version.txt

.PHONY: test
test: build

.PHONY: install
install: test

# Explicit rules
.PHONY: base-clean
base-clean:
	@rm -rf makefile.d

version.txt:
	echo "Update version of ${project_root}/$(project_name)"
	cat version.txt | awk -F. -v OFS=. '{$$NF++;print}' > version.increment
	mv version.increment version.txt

touch-version:
	touch version.txt

depend:
ifdef dependencies
	echo ${project_root}/$(project_name): $(dependencies) > makefile.d
else
	touch makefile.d
endif
