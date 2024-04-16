# This is a convenience script to run the program as-is without installing it
# as a package. make sure all dependencies are installed first.

#!/bin/bash

PYTHON=python3
MODULE_FOLDER=src

PYTHONPATH=$MODULE_FOLDER $PYTHON -m assetbot.assetbot "$@"