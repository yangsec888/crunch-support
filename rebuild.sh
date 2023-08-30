#!/bin/sh
pip uninstall -y crunch_support
python setup.py sdist bdist_wheel
pip install --force-reinstall dist/crunch_support-1.0-py3-none-any.whl