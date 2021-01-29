SHELL = /bin/bash

project_root ?= $(realpath ..)
project_name = $(notdir $(realpath .))
project_version = $(shell cat version.txt)
project_repo ?= ${project_root}/cltl-requirements/leolani
project_mirror ?= ${project_root}/cltl-requirements/mirror

dependencies = $(addprefix $(project_root)/, cltl-requirements)

.DEFAULT_GOAL := install

include $(project_root)/$(project_name)/*.mk


clean: py-clean

install: py-install

.PHONY: docker
docker: py-install
	DOCKER_BUILDKIT=1 docker build -t cltl/${project_name}:${project_version} .