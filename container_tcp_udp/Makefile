SHELL = /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

# Image URL to use all building/pushing image targets
TAG ?= $(shell git describe --tags --abbrev=0 --match 'v[0-9].*[0-9].*[0-9]' 2>/dev/null )
IMG ?= harbor.nooboh.com/prometheus-exporter/container-tcp-dup:$(TAG)

RELEASE_TYPE ?= p
RELEASE_MSG ?= "prometheus exporter"

REL_TAG = $(shell ./scripts/increment_version.sh -${RELEASE_TYPE} ${TAG})

export PATH := $(PWD)/bin:$(PATH)

.DEFAULT_GOAL := help

## clean cache file
clean-pyc: # 查找所有的缓存文件,并清理
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force  {} +

## clean build
clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info

.PHONY:
clean: clean-pyc clean-pyc

.PHONY: lint
lint: # 设置编码规范
	flake8 --exclude=.tox

test: clean-pyc # 测试
	py.test --verbose --color=yes $(TEST_PATH)

## run
run:  depend requirement install
	python3 manager.py

## depend
depend:
	pip3 install pipreqs

## generate requirement.txt
requirement:
	pipreqs exporter --encoding=utf8 --force

## install depend package from requirements.txt
install:
	pip3 install -r exporter/requirements.txt

## Build the docker image
image-build:
	podman build . -t ${IMG}

## Push the docker image
image-push:
	podman push ${IMG}

## check release version
check_release:
	@echo "A new tag (${REL_TAG}) will be pushed to Github, and a new Docker image will be released. Are you sure? [y/N] " && read ans && [ $${ans:-N} == y ]

release: check_release
	git tag -a ${REL_TAG} -m ${RELEASE_MSG}
	git push origin ${REL_TAG}

.PHINY: help
help:
	@echo 'Usage:'
	@echo '  make target'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
    helpMessage = match(lastLine, /^## (.*)/); \
    if (helpMessage) { \
      helpCommand = substr($$1, 0, index($$1, ":")-1); \
      helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
      printf "  %-$(TARGET_MAX_CHAR_NUM)s %s\n", helpCommand, helpMessage; \
    } \
  } \
  { lastLine = $$0 }' $(MAKEFILE_LIST)
