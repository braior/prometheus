SHELL = /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

# Image URL to use all building/pushing image targets
TAG ?= $(shell git describe --tags --abbrev=0 --match 'v[0-9].*[0-9].*[0-9]' 2>/dev/null )
IMG ?= ghcr.io/banzaicloud/kafka-operator:$(TAG)


RELEASE_TYPE ?= p
RELEASE_MSG ?= "prometheus exporter"

REL_TAG = $(shell ./scripts/increment_version.sh -${RELEASE_TYPE} ${TAG})


export PATH := $(PWD)/bin:$(PATH)

# Run against the configured Kubernetes cluster in ~/.kube/config
run:  depend requirement
	python3 main.py

depend:
    pip install pipreqs

requirement:
    pipreqs . --encoding=utf8 --force

# Build the docker image
docker-build:
	docker build . -t ${IMG}

# Push the docker image
docker-push:
	docker push ${IMG}

check_release:
	@echo "A new tag (${REL_TAG}) will be pushed to Github, and a new Docker image will be released. Are you sure? [y/N] " && read ans && [ $${ans:-N} == y ]

release: check_release
	git tag -a ${REL_TAG} -m ${RELEASE_MSG}
	git push origin ${REL_TAG}
