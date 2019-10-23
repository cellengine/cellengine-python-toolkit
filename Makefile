.PHONY: all clean install test test_int test_all uninstall

all: install

clean:
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info

install:
	python setup.py install

test:
	python -m pytest -sv tests/unit

test_this $(test):
	python -m pytest -svvk tests/unit/$(test)

test_int:
	python -m pytest -sv tests/integration --integration

test_all: install
	python -m pytest -sv tests

uninstall:
	pip uninstall cellengine
