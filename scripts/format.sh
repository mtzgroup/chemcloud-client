#!/bin/sh -e

set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place examples tccloud tests examples --exclude=__init__.py
black examples tccloud tests examples
isort examples tccloud tests examples
