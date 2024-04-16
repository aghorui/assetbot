# exporters - exporters for various file formats.
# Copyright (C) 2024 Anamitra Ghorui

import os
from importlib import import_module
import sys
from typing import Dict
from .base import AbstractFileExporter, FileExporterResponse

##
## Contains all exporters available in this module.
##
exporter_list: Dict[str, type[AbstractFileExporter]] = {}

def add_exporters(dir_path: str):
	for module_name in os.listdir(dir_path):
		if module_name == '__init__.py' or module_name == 'base.py'  or module_name[-3:] != '.py':
			continue

		mod = import_module("." + module_name[:-3], package = __name__)
		exporter: type[AbstractFileExporter] = getattr(mod, "Exporter")

		if exporter.NAME in exporter_list:
			print(f"Warning: overriding existing exporter {exporter.NAME} with module from {dir_path}", file = sys.stderr)

		exporter_list[exporter.NAME] = exporter


add_exporters(os.path.dirname(__file__))