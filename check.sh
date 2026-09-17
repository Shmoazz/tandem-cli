#!/bin/sh
# The one command that answers pass or fail. Byte-compile the CLI first, because a
# syntax error there reads as an import failure in every test and hides itself.
set -e
cd "$(dirname "$0")"
python3 -m py_compile tandem
python3 -m unittest -q tandem_test
