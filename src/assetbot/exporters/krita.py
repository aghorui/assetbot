# exporters.krita - Krita .kra to PNG exporter
# Copyright (C) 2024 Anamitra Ghorui

import subprocess
import tempfile
import atexit
import os
from typing import Any, Dict
from zipfile import ZipFile
from pathlib import Path
from .base import MAX_PROCESS_TIMEOUT, AbstractFileExporter, FileExporterOptionSet, FileExporterResponse

# We are creating this as a separate home folder to make krita execute a
# separate instance of itself if one is already running.
# Running parallel krita instances has not been possible since krita 5.2
# without a workaround like this.
class ExporterGlobalContextSingleton:
	def __init__(self):
		krita_tmp_home = tempfile.TemporaryDirectory(prefix = "aw_krita_exporter")
		atexit.register(krita_tmp_home.cleanup)

		self.krita_env = os.environ.copy()
		self.krita_env["HOME"] = krita_tmp_home.name


class Exporter(AbstractFileExporter):
	NAME = "krita"
	DESCRIPTION = "Exports a krita .kra file to png"
	PATTERNS = [ "*.kra" ]

	GLOBAL_CONTEXT = ExporterGlobalContextSingleton()
	KRITA_EXEC_NAME = "krita"
	DEFAULT_SUFFIX = ".png"

	OPTIONS = FileExporterOptionSet(
		("suffix", str, "specify extension of the exported file", DEFAULT_SUFFIX)
	)

	def __init__(self, options: Dict[str, Any] = {}) -> None:
		super().__init__(options)

		self.suffix = options["suffix"] if "suffix" in options else self.DEFAULT_SUFFIX

	def export(self, src_path: Path, dest_path: Path, name: str) -> FileExporterResponse:
		dest_full_path = dest_path.joinpath(name).with_suffix(self.suffix)

		with ZipFile(src_path) as file:
			# if this is not an animation, we can just extract the merged image from it
			if len(list(filter(lambda x: x.find("/animation/") >= 0, file.namelist()))) == 0:
				file.extract("mergedimage.png", dest_path)
				return FileExporterResponse(dest_path = dest_full_path)

		proc = subprocess.Popen(
			[
				self.KRITA_EXEC_NAME,
				"--export",
				"--export-filename", dest_full_path,
				src_path
			],
			env    = self.GLOBAL_CONTEXT.krita_env,
			stdin  = None,
			stdout = subprocess.PIPE,
			stderr = subprocess.STDOUT
		)

		output_log = proc.communicate(timeout = MAX_PROCESS_TIMEOUT)[0]

		if proc.returncode != 0:
			return FileExporterResponse(
				message = f"Export process failed with statuscode: {proc.returncode}",
				output_log = output_log.decode(),
				dest_path = dest_full_path,
				success = False
			)

		return FileExporterResponse(
			output_log = output_log.decode(),
			dest_path = dest_full_path
		)