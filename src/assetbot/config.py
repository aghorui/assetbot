# config.py -
# Copyright (C) 2024 Anamitra Ghorui

import argparse
import sys
import toml
from typing import List, Dict, Literal

class TestError(Exception):
	def __init__(self, message: str):
		self.message = message


def test(value, message):
	if not value:
		raise TestError(message)

class Config:

	@classmethod
	def default(cls):
		return cls()


	def __repr__(self):
		return str(vars(self))

	def __init__(self,
		config: str = "",
		dump_default_config: bool = False,
		list_exporters: bool = False,
		ignore_delete: bool = False,
		working_dir: str = ".",
		log_level: Literal["normal", "silent", "verbose"] = "normal",
		path_mappings: List[List[str]] = [],
		allowed_exporters: List[str] = [],
		patterns: List[Dict] = [],
		ignore_patterns: List[str] = [],
		exporters: Dict[str, Dict] = {}
	):
		try:
			test(isinstance(ignore_delete, bool),
				"ignore_delete should either be 'true' or 'false'")
			self.ignore_delete   =  ignore_delete

			test(isinstance(working_dir, str),
				"working_dir should be a string")
			self.working_dir     =  working_dir

			test(isinstance(log_level, str) and (log_level in ["normal", "silent", "verbose"]),
				"log_level should be either 'normal', 'silent' or 'verbose'")
			self.log_level = log_level

			test(isinstance(path_mappings, list),
				"path_mappings should be a list of entries")
			for i in path_mappings:
				test((isinstance(i, list) or isinstance(i, tuple)) and len(i) == 2,
					"each entry in path_mappings has to be a list of 2 elements")
			self.path_mappings   =  path_mappings

			test(isinstance(allowed_exporters, list),
				"allowed_exporters should be a list of strings")
			for i in allowed_exporters:
				test(isinstance(i, str),
					"each entry in allowed_exporters has to be a string")
			self.allowed_exporters = allowed_exporters

			test(isinstance(allowed_exporters, list),
				"ignore_patterns should be a list of strings")
			for i in allowed_exporters:
				test(isinstance(i, str),
					"each entry in allowed_exporters has to be a string")
			self.ignore_patterns =  ignore_patterns

			for i in exporters.keys():
				test(isinstance(i, str), "each exporter name should be a string")
				test(isinstance(exporters[i], dict),
					f"'exporters.{i}' is not a list of key-value pairs.")
			self.exporters = exporters

		except TestError as e:
			raise e

def read_config_file(path: str) -> Dict:
	with open(path) as f:
		config_dict = toml.load(f)
		return config_dict

def read_args() -> Dict:
	parser = argparse.ArgumentParser(
		prog        = sys.argv[0],
		description = "Watch for and export your assets to a desired location.",
		epilog      =
			"Flags specified via a commandline invocation of this application " +
			"take precedence over the config file, if one is given.")

	parser.add_argument(
		"--config", "-c",
		metavar = "path",
		type    = str,
		help    = "Path to config file"
	)

	parser.add_argument(
		"--working_dir", "-wd",
		metavar = "path",
		type    = str,
		default = argparse.SUPPRESS,
		help    = "Working directory for the program"
	)

	parser.add_argument(
		"--map_path", "-m",
		nargs   = 2,
		action  = "append",
		dest    = "path_mappings",
		metavar = ("src", "dest"),
		type    = str,
		default = argparse.SUPPRESS,
		help    =
			"Specify a folder where the program will listen for changes," +
			"and another folder where it will export to."
	)

	parser.add_argument(
		"--allowed_exporters", "-e",
		nargs   = "*",
		dest    = "allowed_exporters",
		metavar = "exporter",
		type    = str,
		default = argparse.SUPPRESS,
		help    =
			"Specify the exporters to use."
	)

	# parser.add_argument(
	# 	"--add_pattern", "-p",
	# 	nargs   = 3,
	# 	action  = "append",
	# 	dest    = "",
	# 	metavar = ("exporter", "option", "value"),
	# 	type    = str,
	# 	help    = "Specify a filename pattern and an exporter for it."
	# )

	parser.add_argument(
		"--log_level", "-l",
		choices = ("silent", "normal", "verbose"),
		default = argparse.SUPPRESS,
		help    = "Set logging level"
	)

	parser.add_argument(
		"--dump_default_config",
		action = 'store_true',
		default = argparse.SUPPRESS,
		help   = "Dump the default config file and exit"
	)

	parser.add_argument(
		"--ignore_delete",
		action  = 'store_true',
		default = argparse.SUPPRESS,
		help    = "Do not do anything when a source file is deleted"
	)

	parser.add_argument(
		"--list_exporters",
		action  = 'store_true',
		default = argparse.SUPPRESS,
		help    = "List all currently available exporters within the program"
	)

	args = parser.parse_args()

	return vars(args)