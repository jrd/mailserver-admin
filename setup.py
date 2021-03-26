from configparser import ConfigParser
from json import loads
from pathlib import Path

from setuptools import (
    find_packages,
    setup,
)

# https://github.com/pypa/sampleproject/blob/master/setup.py
# https://packaging.python.org/guides/distributing-packages-using-setuptools


# taken from https://github.com/gsemet/pipenv-to-requirements/blob/master/pipenv_to_requirements/__init__.py
def pkg_clean_version(pkg_name, pkg_info):
    if pkg_info.startswith('{'):
        pkg_info = loads(pkg_info)
    else:
        return pkg_name if pkg_info.strip() == "*" else f"{pkg_name}{pkg_info}"
    if not pkg_info:
        return pkg_name
    version = pkg_info.get("version", "").strip()
    editable = pkg_info.get("editable", False)
    markers = pkg_info["markers"].strip() if pkg_info.get("markers") else ""
    extras = pkg_info.get("extras", [])
    subdir = pkg_info.get("subdirectory", [])
    git = pkg_info.get("git", "").strip()
    path = pkg_info.get("path", "").strip()
    ref = pkg_info.get("ref", "").strip()
    rstr = ""
    if not editable:
        rstr += pkg_name
    if extras:
        rstr += "[{}]".format(', '.join([s.strip() for s in extras]))
    if not editable:
        if version and version != "*":
            rstr += version.strip()
    elif git:
        ref = "@" + ref if ref else ref
        rstr = "-e git+" + git + ref + "#egg=" + pkg_name
        if subdir:
            rstr += '&subdirectory=' + subdir
    else:
        rstr = "-e " + path
    if markers:
        rstr += " ; " + markers
    return rstr


def parse_pip_file(pipfile):
    config = ConfigParser()
    config.read(pipfile)
    return [
        pkg_clean_version(name.strip('"'), info.strip('"'))
        for name, info in config._sections.get('packages', {}).items()
    ]


def parse_extra_pip_file(pipfile):
    pipfile_path = Path(pipfile)
    if pipfile_path.exists():
        config = ConfigParser()
        config.read(pipfile_path)
        return {
            section: [pkg_clean_version(name.strip('"'), info.strip('"')) for name, info in config[section].items()]
            for section in config.sections()
        }
    else:
        return {}


requirements = parse_pip_file('Pipfile')
extras = parse_extra_pip_file('Pipfile.extra')

setup(
    # packages=find_packages(where='.'),
    # package_dir={'': '.'},
    # include_package_data=True,
    install_requires=requirements,
    extras_require=extras,
)
