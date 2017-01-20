all:    clean build

pypi:   clean build upload

upload:
	twine upload dist/*

build:
	rm -rf build/ dist/
	python setup.py bdist_wheel

clean:
	find . -type d -name __pycache__ | xargs rm -rf
	find . -type f -name "*.pyc" -delete
	rm -rf dist/ build/
	rm -rf *.egg-info
	rm -rf ignoreme build dist
	rm -rf tmp

