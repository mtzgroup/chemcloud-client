#!/bin/sh -e

set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place examples chemcloud tests examples --exclude=__init__.py
black examples chemcloud tests examples
isort examples chemcloud tests examples
