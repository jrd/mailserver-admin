.PHONY: default clean venv bump_version build twine test_upload pypi_upload

default:
	@echo "make TARGET"
	@echo ""
	@echo "TARGETS:"
	@echo "  clean: delete all generated files"
	@echo "  bump_version: use the 'what' variable to define what to bump: major, minor or patch"
	@echo "  build: create source and wheel packages"
	@echo "  test_upload: build and upload packages to testpypi (always do this first)"
	@echo "  pypi_upload: build and upload packages to pypi"

clean:
	@rm -rf build dist mailserveradmin/to_serve *.egg-info 2>/dev/null
	@find . -type d -name __pycache__ -prune -exec rm -rf '{}' \;

venv:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
	    echo "You should activate the virtualenv: pipenv shell" >&2; \
	    exit 1; \
	fi

mailserveradmin/to_serve:
	@mkdir -p mailserveradmin/to_serve; \
	python -m django collectstatic --noinput && \
	mv static mailserveradmin/to_serve/ && \
	( \
	cd mailserveradmin/to_serve/static && \
	find fontawesome_free -mindepth 1 -maxdepth 1 -type d -not \( -name 'css' -o -name 'webfonts' \) -exec rm -rf '{}' \; \
	)

bump_version: venv
	@if ! echo "$(what)" | grep -q '^major\|minor\|patch$$'; then \
	    echo "You should specify 'what' variable with one of major, minor or patch" >&2; \
	    exit 1; \
	fi; \
	VER_MODULE="$$(sed -rn '/^version =/{s/.* attr: (.*)/\1/p}' setup.cfg | rev | cut -d. -f2- | rev)"; \
	VER_VAR="$$(sed -rn '/^version =/{s/.* attr: (.*)/\1/p}' setup.cfg | rev | cut -d. -f1 | rev)"; \
	NEW_VER="$$(python -c 'from '$${VER_MODULE}' import '$${VER_VAR}' as ver; from semver import parse_version_info; print(parse_version_info(ver).bump_$(what)())')"; \
	OLD_VER="$$(python -c 'from '$${VER_MODULE}' import '$${VER_VAR}' as ver; print(ver)')"; \
	echo "$${OLD_VER} → $${NEW_VER}"; \
	sed -ri "/^$${VER_VAR} =/{s/'.*'/'$${NEW_VER}'/}" $${VER_MODULE}/__init__.py

build: clean venv mailserveradmin/to_serve
	python setup.py sdist bdist_wheel

twine: venv
	@pip freeze | grep -q ^twine= >/dev/null || pip install twine

test_upload: build twine
	python -m twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*

pypi_upload: build twine
	python -m twine upload dist/*
