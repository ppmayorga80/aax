#!/bin/bash
#define python version, if you want another version execute
#export PYTHON="python3.20"
#bash install.sh
echo "defining python version: PYTHON=$PYTHON"
if [[ $PYTHON == "" ]]; then
  echo "PYTHON is empty, default is python3.10"
  PYTHON="python3.10"
fi
echo "python version is:"
echo "PYTHON=$PYTHON"

if [ ! -d .venv ]; then
  echo "Creating venv"
  $PYTHON -m venv .venv
else
  echo "venv already exists"
fi

echo "activating environment"
. .venv/bin/activate

if [[ ! $PYTHONPATH =~ $PWD ]]; then
  echo "Exporting PYTHONPATH"
  export PYTHONPATH="$PWD:$PYTHONPATH"
else
  echo "PYTHONPATH is defined"
fi
echo "PYTHONPATH=$PYTHONPATH"

echo "installing libraries"
pip install --upgrade pip
pip install -r requirements.txt

echo "DONE"