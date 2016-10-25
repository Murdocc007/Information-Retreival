#!/bin/bash
wget https://bootstrap.pypa.io/get-pip.py
export PYTHONHOME=/usr
python get-pip.py --user
export PATH=$HOME/.local/bin:$PATH
pip install -U nltk --user
python -m nltk.downloader wordnet

