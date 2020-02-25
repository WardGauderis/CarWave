#!/usr/bin/env sh
git pull && flask db migrate && flask db upgrade

