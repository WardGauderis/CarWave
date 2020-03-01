#!/usr/bin/env sh
(. env/bin/activate || . venv/bin/activate) && git pull && flask db migrate && flask db upgrade

