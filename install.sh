#!/bin/sh
git submodule update --init --recursive
xsdata generate -p netex  --unsafe-hash -ss clusters --compound-fields  xsd/NeTEx/xsd/NeTEx_publication.xsd
