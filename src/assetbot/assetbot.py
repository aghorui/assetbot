# assetbot - Watch for and export your assets to a desired location.
# Copyright (C) 2024 Anamitra Ghorui


# Just to clarify: All mentions of patterns here refer to Globs. Regexes will
# be explicitly refered to as regexes.

import os
import sys
import json
import time
import signal
import logging
from pathlib import Path
from glob import glob
from typing import Dict, List, Literal
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers.api import BaseObserver, BaseObserverSubclassCallable, ObservedWatch
from .config import read_config_file, read_args, Config
from .exporters import AbstractFileExporter, exporter_list, add_exporters

VERSION = "0.1.1"

def message(*args, **kwargs):
	print(*args, file = sys.stderr, **kwargs)

def compact_time(time_sec: float) -> str:
	"""
	Converts time in seconds to a compact representation for use with this
	application.

	:param      time_sec:  Time in seconds
	:type       time_sec:  float

	:returns:   { The time representation }
	:rtype:     str
	"""
	if time_sec < 1:
		return "%0.2f ms" % ( time_sec * 1000 )
	else:
		return "%0.2f sec" % ( time_sec )

def class_to_name(c) -> str:
	"""
	Converts a class to a human-readable name. Used for displaying the
	data types of exporter parameters.

	:param      c:    The class

	:returns:   Custom string representation of the class
	:rtype:     str
	"""
	if   c == int:   return "int"
	elif c == float: return "float"
	elif c == str:   return "string"
	elif c == list:  return "list"
	elif c == bool:  return "true/false"
	else: return "INVALID"

class FileUpdateHandler(PatternMatchingEventHandler):
	"""
	Watches for files, matches them based on a regex and runs the export on
	them.
	"""

	def __init__(self,
		exporter: AbstractFileExporter,
		src_base_path: str,
		dest_base_path: str,
		patterns           = None,
		ignore_patterns    = None,
		ignore_directories = False,
		case_sensitive     = False):
		super().__init__(
			patterns,
			ignore_patterns,
			ignore_directories,
			case_sensitive)

		self.src_base_path  = src_base_path
		self.dest_base_path = dest_base_path
		self.exporter       = exporter

	def run_export(self, event: FileSystemEvent) -> None:
		"""
		Common function for running the export. Invoked in the other overridable
		functions of the superclass.

		:param      event:  The event
		:type       event:  FileSystemEvent
		"""

		# Determine source and destination paths.
		src_path = Path(event.src_path).relative_to(self.src_base_path)
		dest_path = Path(self.dest_base_path).joinpath(src_path.parent)
		dest_path.mkdir(parents = True, exist_ok = True)

		logging.info(f"EXPORT {src_path} -> {dest_path}")

		# Call the exporter, and log the time.
		start_time = time.time()
		response = self.exporter.export(Path(event.src_path), dest_path, src_path.stem)
		end_time = time.time()
		elapsed = compact_time(end_time - start_time)

		if response.success:
			logging.info(f"DONE   {src_path} -> {response.dest_path} in {elapsed}")
		else:
			logging.error(f"ERROR  {response.message}")
			logging.error(f"Log:\n\n{response.output_log}")


	def on_created(self, event: FileSystemEvent) -> None:
		super().on_created(event)
		logging.info(f"CREATE {event.src_path} ")
		self.run_export(event)


	def on_modified(self, event: FileSystemEvent) -> None:
		super().on_modified(event)
		logging.info(f"UPDATE {event.src_path} ")
		self.run_export(event)


# This acts as a mutable pointer object.
# Used for setting the terminate flag.
class Box:
	def __init__(self, value):
		self.value = value

def main():
	# The object that holds all the configuration details
	config: Config

	# Read command-line arguments
	arg_config = read_args()

	# Prepare the config object
	if "config" in arg_config and arg_config["config"] != None:
		try:
			file_config = read_config_file(arg_config["config"])
		except FileNotFoundError:
			message(f"Error: File not found: '{arg_config['config']}'")
			sys.exit(1)

		for k in arg_config:
			file_config[k] = arg_config[k]

		config = Config(**file_config)
	else:
		config = Config(**arg_config)

	if config.working_dir != "":
		os.chdir(config.working_dir)

	# Add additional exporters if available
	if len(config.exporter_paths) > 0:
		for path in config.exporter_paths:
			add_exporters(path)

	if "dump_default_config" in arg_config and arg_config["dump_default_config"] == True:
		print(open(os.path.join(os.path.dirname(__file__), "example_config.toml")).read())
		sys.exit(0)

	if "list_exporters" in arg_config and arg_config["list_exporters"] == True:
		for e in exporter_list.values():
			print("Name:", e.NAME)
			print("Desc:", e.DESCRIPTION)
			print("Patterns:", ", ".join(map(lambda x: f"'{x}'", e.PATTERNS)) if len(e.PATTERNS) > 0 else "<none>")
			print("Options:")
			for i in e.OPTIONS.values():
				print(f"  '{i.name}': <{class_to_name(i.value_type)}> {i.desc}", end = "")
				if i.default != None:
					print(f" (default: {i.default})", end = "")
			print(end = "\n\n")

		print("All exporters support the following options:")

		for i in AbstractFileExporter.OPTIONS.values():
			print(f"  '{i.name}': <{class_to_name(i.value_type)}> {i.desc}", end = "")
			if i.default != None:
				print(f" (default: {i.default})", end = "")

		print(end = "\n\n")

		sys.exit(0)


	# setup termination flag
	terminate_flag = Box(False)

	def set_terminate_flag(_signum, _frame):
		terminate_flag.value = True

	message(f"assetbot version {VERSION}")
	message("Working directory:", os.getcwd())


	if config.log_level == "silent":
		logging.disable(logging.INFO)

	# TODO Do something for loglevel normal and verbose

	logging.basicConfig(
		level   = logging.INFO,
		format  = '%(asctime)s - %(message)s',
		datefmt = '%Y-%m-%d %H:%M:%S')

	observer: BaseObserver | None = None

	if not config.init_only:
		observer = Observer()

	# message("Available exporters: ", ", ".join(exporter_list.keys()))


	if len(config.allowed_exporters) == 0:
		message("Please specify the exporters that you want to use.")
		sys.exit(1)

	message("Current exporters:", ", ".join(config.allowed_exporters))

	if len(config.ignore_patterns) > 0:
		message("Ignored file patterns:", ", ".join(config.ignore_patterns))

	# Initialize the exporter
	for exporter in config.allowed_exporters:
		if not (exporter in exporter_list):
			message(f"Exporter '{exporter}' not found.")
			sys.exit(1)

		exporter_class: type[AbstractFileExporter] = exporter_list[exporter]
		exporter_instance: AbstractFileExporter
		exporter_options = config.exporters[exporter] if exporter in config.exporters else dict()

		try:
			exporter_instance = exporter_class(exporter_options)
		except Exception as e:
			message("Error while initializing exporter: ", getattr(e, 'message', repr(e)))
			sys.exit(1)

		# Now listen on all paths with this exporter
		for (src_path, dest_path) in config.path_mappings:
			if not (Path(src_path).exists() and Path(src_path).is_dir()):
				message(f"Source path {src_path} not found.")
				sys.exit(1)

			if not (Path(dest_path).exists() and Path(dest_path).is_dir()):
				message(f"Source path {src_path} not found.")
				sys.exit(1)

			handler = FileUpdateHandler(
				exporter_instance,
				src_path,
				dest_path,
				patterns = exporter_instance.file_patterns,
				ignore_patterns = config.ignore_patterns,
				ignore_directories = True
			)

			if not config.no_init:
				for pattern in exporter_instance.file_patterns:
					for filename in glob(os.path.join(src_path, "**", pattern), recursive = True):
						handler.run_export(FileSystemEvent(filename))

			if not config.init_only and observer != None:
				observer.schedule(handler, src_path, recursive = True)

	if config.init_only:
		message("Init done. Exiting.")
		sys.exit(0)
		return

	# If this is true, it is a bug.
	assert observer != None, "Observer should never be null at this point."

	# Now start the watcher
	observer.start()

	message("Watcher started for the following mappings:")

	for (src_path, dest_path) in config.path_mappings:
		message(f"{src_path} -> {dest_path}")

	print()

	# Everything is set up. Activate the termination signal trigger.
	signal.signal(signal.SIGTERM, set_terminate_flag)

	# Listen for an interrupt or sigterm
	try:
		while not terminate_flag.value:
			time.sleep(1)
	except KeyboardInterrupt:
		message("Interrupt detected.")
		observer.stop()

	message("Exiting.")
	observer.join()


if __name__ == "__main__":
	main()