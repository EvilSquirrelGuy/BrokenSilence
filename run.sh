#! /usr/bin/env sh

if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/python3 -m pip install -r requirements.txt
fi

.venv/bin/python3 main.py