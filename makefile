SHELL = /bin/bash

project_dependencies ?= $(addprefix $(project_root)/, emissor cltl-requirements)

git_remote ?= https://github.com/leolani


include util/make/makefile.base.mk
include util/make/makefile.component.mk
include util/make/makefile.py.base.mk
include util/make/makefile.git.mk

.PHONY: docker-ghcr-build docker-ghcr-push
docker-ghcr-build docker-ghcr-push:
	$(info No Docker image for $(project_name))
