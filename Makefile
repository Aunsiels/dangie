PYTHON ?= python3

.EXPORT_ALL_VARIABLES:

PYTHONPATH = PYTHONPATH:$(pwd)

build:
	rm -f dist/*
	$(PYTHON) setup.py sdist bdist_wheel

.PHONY: build
