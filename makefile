PROJECT = mophidian

install:
	pip3 install -e .

all:
	make install format lint

format:
	isort $(PROJECT) && black $(PROJECT)

lint:
	pylint $(PROJECT)

type:
	mypy $(PROJECT)

test:
	pytest --cov="./$(PROJECT)" tests/

cover:
	coverage html

test-cov:
	make test cover

build_docs:
	pdoc $(PROJECT) -d google -o docs/

build:
	python3 -m build

deploy:
	python3 -m twine upload --repository pypi dist/*

build_deploy:
	make build deploy