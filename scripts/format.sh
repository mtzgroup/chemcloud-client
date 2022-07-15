#!/bin/sh -e

set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place examples qccloud tests examples --exclude=__init__.py
black examples qccloud tests examples
isort examples qccloud tests examples
