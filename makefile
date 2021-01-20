SHELL = /bin/bash


project_root ?= $(realpath ..)
project_name = $(notdir $(realpath .))
project_version ?= "0.0.1-dev"
project_repo ?= ${project_root}/cltl-requirements/leolani
proj = $(project_root)/$(project_name)


.DEFAULT_GOAL := install

.PHONY: depend
depend:
	touch makefile.d

.PHONY: clean
clean:
	rm -rf dist

venv:
	python -m venv venv
	source venv/bin/activate; \
		pip install -r requirements.txt

dist: cltl venv
	source venv/bin/activate; \
		python setup.py sdist; \
		deactivate

.PHONY: install
install: dist
	cp dist/*.tar.gz $(project_repo)

.PHONY: docker
docker: install
	DOCKER_BUILDKIT=1 docker build -t cltl/${project_name}:${project_version} .
