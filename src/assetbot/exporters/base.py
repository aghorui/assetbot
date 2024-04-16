# base.py - base classes for exporter implementations
# Copyright (C) 2024 Anamitra Ghorui

from pathlib import Path
from typing import Any, Dict, List, Tuple, Type

MAX_PROCESS_TIMEOUT = 1000

class FileExporterResponse:
	"""
	Response returned by an AbstractFileExporter.
	"""
	def __init__(self,
		message               = "",
		output_log: str       = "",
		dest_path: Path | str = "",
		success: bool         = True):
		self.message    = message
		self.output_log = output_log
		self.success    = success
		self.dest_path  = dest_path


FileExporterOptionType =  type[str | bool | int | float | list | None]


class FileExporterOption:
	"""
	Describes a file exporter option with its name, description and type.
	"""

	def __init__(self,
		name: str,
		value_type: FileExporterOptionType,
		desc: str = "",
		default: Any = None):
		self.name = name
		self.value_type = value_type
		self.desc = desc
		self.default = default


class FileExporterOptionSet:
	"""
	Describes a set of file exporter options.
	"""

	def extend(self, *args: Tuple[str, FileExporterOptionType, str, Any]):
		for entry in args:
			self.option_list[entry[0]] = FileExporterOption(
				entry[0], entry[1], entry[2], entry[3]
			)

	def __init__(self, *args: Tuple[str, FileExporterOptionType, str, Any]):
		self.option_list: Dict[str, FileExporterOption] = dict()
		self.extend(*args)

	def __getitem__(self, key: str) -> FileExporterOption:
		return self.option_list[key]

	def __contains__(self, key: str) -> bool:
		return key in self.option_list

	def __iter__(self):
		return iter(self.option_list)

	def values(self):
		return self.option_list.values()


class AbstractFileExporter:
	"""
	Abstract class to implement a file exporter for use with the watcher.
	"""

	## Name used as the identifier for the exporter.
	NAME: str = "invalid"

	## Short description of the exporter.
	DESCRIPTION: str = "invalid"

	## List of regexes (as strings) accepted by the exporter.
	PATTERNS: List[str] = []

	## The list of options this exporter accepts.
	OPTIONS: FileExporterOptionSet = FileExporterOptionSet(
		("patterns", list, "set the patterns this exporter will match for", None)
	)

	def __init__(self, options: Dict[str, Any] = {}) -> None:
		self.options = self.OPTIONS
		self.file_patterns = options["patterns"] if "patterns" in options else self.PATTERNS

	def get_option_list(self) -> FileExporterOptionSet:
		return self.options

	def export(self, src_path: Path, dest_path: Path, name: str) -> FileExporterResponse:
		"""
		Exports file at src_path to dest_path with filename 'name'

		:param      src_path:   The source path
		:type       src_path:   Path
		:param      dest_path:  The destination path
		:type       dest_path:  Path
		:param      name:       The name
		:type       name:       str

		:returns:   A tuple with the destination file path and the log.
		:rtype:     (str, str)
		"""
		raise NotImplementedError