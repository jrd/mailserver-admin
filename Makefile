.PHONY: default clean bump_version build twine test_upload pypi_upload image docker_upload semver

default:
	@echo "make TARGET"
	@echo ""
	@echo "TARGETS:"
	@echo "  clean: delete all generated files"
	@echo "  bump_version: use the 'what' variable to define what to bump: major, minor or patch"
	@echo "  build: create source and wheel packages"
	@echo "  test_upload: build and upload packages to testpypi (always do this first)"
	@echo "  pypi_upload: build and upload packages to pypi"
	@echo "  image: build docker image"
	@echo "  docker_upload: upload docker image"

clean:
	@rm -rf build dist mailserveradmin/to_serve *.egg-info 2>/dev/null
	@find . -type d -name __pycache__ -prune -exec rm -rf '{}' \;

mailserveradmin/to_serve:
	@mkdir -p mailserveradmin/to_serve; \
	python -m django collectstatic --noinput && \
	mv static mailserveradmin/to_serve/ && \
	( \
	cd mailserveradmin/to_serve/static && \
	find fontawesome_free -mindepth 1 -maxdepth 1 -type d -not \( -name 'css' -o -name 'webfonts' \) -exec rm -rf '{}' \; \
	)

semver:
	@pipenv run pip freeze | grep -q ^semver= >/dev/null || pipenv run pip install semver

bump_version: semver
	@if ! echo "$(what)" | grep -q '^major\|minor\|patch$$'; then \
	    echo "You should specify 'what' variable with one of major, minor or patch" >&2; \
	    exit 1; \
	fi; \
	VER_MODULE="$$(sed -rn '/^version =/{s/.* attr: (.*)/\1/p}' setup.cfg | rev | cut -d. -f2- | rev)"; \
	VER_VAR="$$(sed -rn '/^version =/{s/.* attr: (.*)/\1/p}' setup.cfg | rev | cut -d. -f1 | rev)"; \
	NEW_VER="$$(pipenv run python -c 'from '$${VER_MODULE}' import '$${VER_VAR}' as ver; from semver import parse_version_info; print(parse_version_info(ver).bump_$(what)())')"; \
	OLD_VER="$$(python -c 'from '$${VER_MODULE}' import '$${VER_VAR}' as ver; print(ver)')"; \
	echo "$${OLD_VER} → $${NEW_VER}"; \
	sed -ri "/^$${VER_VAR} =/{s/'.*'/'$${NEW_VER}'/}" $${VER_MODULE}/__init__.py

build: clean mailserveradmin/to_serve
	pipenv run python setup.py sdist bdist_wheel

twine:
	@pipenv run pip freeze | grep -q ^twine= >/dev/null || pipenv run pip install twine

test_upload: build twine
	pipenv run python -m twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*

pypi_upload: build twine
	pipenv run python -m twine upload dist/*

image:
	@VER_MODULE="$$(sed -rn '/^version =/{s/.* attr: (.*)/\1/p}' setup.cfg | rev | cut -d. -f2- | rev)"; \
	VER_VAR="$$(sed -rn '/^version =/{s/.* attr: (.*)/\1/p}' setup.cfg | rev | cut -d. -f1 | rev)"; \
	VER="$$(python -c 'from '$${VER_MODULE}' import '$${VER_VAR}' as ver; print(ver)')"; \
	export DOCKER_BUILDKIT=1; \
	echo Building jrdasm/mailserver-admin:$${VER} && \
	docker build --no-cache --pull --build-arg GIT_TAG=$${VER} -t jrdasm/mailserver-admin:$${VER} .

docker_upload:
	@VER_MODULE="$$(sed -rn '/^version =/{s/.* attr: (.*)/\1/p}' setup.cfg | rev | cut -d. -f2- | rev)"; \
	VER_VAR="$$(sed -rn '/^version =/{s/.* attr: (.*)/\1/p}' setup.cfg | rev | cut -d. -f1 | rev)"; \
	VER="$$(python -c 'from '$${VER_MODULE}' import '$${VER_VAR}' as ver; print(ver)')"; \
	docker push jrdasm/mailserver-admin:$${VER}
