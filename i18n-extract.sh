#!/bin/sh

exec pybabel extract \
    --project=pycerberus \
    --version=`cat VERSION.txt` \
    --copyright-holder="Felix Schwarz" \
    --msgid-bugs-address="felix.schwarz@oss.schwarz.eu" \
    --keywords="_ ngettext:1,2 N_ tag_ tagn_:1,2" \
    --add-comments="TRANSLATOR:" \
    --output-file=pycerberus/locales/pycerberus.pot \
    pycerberus
