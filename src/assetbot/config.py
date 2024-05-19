# config.py - Configuration loading routines
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
		init_only: bool = False,
		no_init: bool = False,
		working_dir: str = "",
		log_level: Literal["normal", "silent", "verbose"] = "normal",
		delete_behavior: Literal["ignore", "delete"] = "ignore",
		path_mappings: List[List[str]] = [],
		allowed_exporters: List[str] = [],
		exporter_paths: List[str] = [],
		ignore_patterns: List[str] = [],
		exporters: Dict[str, Dict] = {}
	):
		try:
			test(isinstance(init_only, bool),
				"init_only should be either 'true' or 'false'")
			self.init_only = init_only

			test(isinstance(no_init, bool),
				"no_init should be either 'true' or 'false'")
			self.no_init = no_init

			test(isinstance(list_exporters, bool),
				"list_exporters should be either 'true' or 'false'")
			self.list_exporters = list_exporters

			test(isinstance(dump_default_config, bool),
				"dump_default_config should be either 'true' or 'false'")
			self.dump_default_config = dump_default_config

			test(isinstance(delete_behavior, str),
				"delete_behavior should either be 'ignore' or 'delete'")
			self.delete_behavior  =  delete_behavior

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

			test(isinstance(exporter_paths, list),
				"allowed_exporters should be a list of strings")
			for i in exporter_paths:
				test(isinstance(i, str),
					"each entry in allowed_exporters has to be a string")
			self.exporter_paths = exporter_paths

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
		prog        = "assetbot",
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
		"--working-dir", "-wd",
		metavar = "path",
		dest    = "working_dir",
		type    = str,
		default = argparse.SUPPRESS,
		help    = "Working directory for the program"
	)

	parser.add_argument(
		"--map-path", "-m",
		nargs   = 2,
		action  = "append",
		dest    = "path_mappings",
		metavar = ("src", "dest"),
		type    = str,
		default = argparse.SUPPRESS,
		help    =
			"Specify a folder where the program will listen for changes " +
			"and another folder where it will export to"
	)

	parser.add_argument(
		"--exporter-paths", "-ep",
		nargs   = "*",
		dest    = "exporter_paths",
		metavar = "path",
		type    = str,
		default = argparse.SUPPRESS,
		help    =
			"Specify the directories from which to load exporters from"
	)

	parser.add_argument(
		"--allowed-exporters", "-e",
		nargs   = "*",
		dest    = "allowed_exporters",
		metavar = "exporter",
		type    = str,
		default = argparse.SUPPRESS,
		help    =
			"Specify the exporters to use"
	)

	parser.add_argument(
		"--delete-behavior",
		dest    = "delete_behavior",
		choices = ("ignore", "delete"),
		default = argparse.SUPPRESS,
		help    = "What to do when a file is deleted. (Default: ignore)"
	)

	parser.add_argument(
		"--ignore-patterns", "-ig",
		nargs   = "*",
		dest    = "ignore_patterns",
		choices = ("ignore", "delete"),
		metavar = "pattern",
		type    = str,
		default = argparse.SUPPRESS,
		help    =
			"Specify the exporters to use"
	)

	parser.add_argument(
		"--log-level", "-l",
		dest    = "log_level",
		choices = ("silent", "normal", "verbose"),
		default = argparse.SUPPRESS,
		help    = "Set logging level"
	)

	parser.add_argument(
		"--dump-default-config",
		action  = 'store_true',
		default = argparse.SUPPRESS,
		help    = "Dump the default config file and exit"
	)

	init_group = parser.add_mutually_exclusive_group()

	init_group.add_argument(
		"--init-only",
		dest    = "init_only",
		action  = 'store_true',
		default = argparse.SUPPRESS,
		help    = "Only perform the initial export and exit"
	)

	init_group.add_argument(
		"--no-init",
		dest    = "no_init",
		action  = 'store_true',
		default = argparse.SUPPRESS,
		help    = "Do not perform the initial export"
	)

	parser.add_argument(
		"--list-exporters",
		dest    = "list_exporters",
		action  = 'store_true',
		default = argparse.SUPPRESS,
		help    =
			"List all currently available exporters within the program and exit"
	)

	args = parser.parse_args()

	return vars(args)