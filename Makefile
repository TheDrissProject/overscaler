
help:
	@echo "Makefile Options:"
	@echo "\t- clean: Remove all build, test, coverage and Python artifacts"
	@echo "\t- install: Install the package to the active Python's site-packages"
	@echo "\t- pip-install: Use pip to install the package to the active Python's site-packages"
	@echo "\t- test: Run tests quickly with Pytest"
	@echo "\t- coverage: Check code coverage with all tests"

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage

test: ## run tests quickly with the default Python
	python3 setup.py test
	rm -fr .eggs/

coverage: ## check code coverage quickly with the default Python
	coverage run --source overscaler setup.py test
	coverage report -m
	@rm -fr .eggs/

install: clean ## install the package to the active Python's site-packages
	sudo python3 setup.py install

pip-install: clean ## install the package using pip.
	pip3 install -e .

docu: ## check code coverage quickly with the default Python
	rm -f docs/overscaler.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ overscaler
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
