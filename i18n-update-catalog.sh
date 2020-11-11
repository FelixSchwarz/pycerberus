#!/bin/sh

exec pybabel update \
    --domain=pycerberus \
    --input-file=pycerberus/locales/pycerberus.pot \
    --output-dir=pycerberus/locales


