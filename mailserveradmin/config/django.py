from os import environ
from sys import argv

from django.core.management import execute_from_command_line


def main():
    """Run django management commands."""
    environ.setdefault('DJANGO_SETTINGS_MODULE', 'mailserveradmin.config.settings')
    execute_from_command_line(argv)
