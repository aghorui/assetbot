# exporters.svg - Inkscape SVG to Plain SVG exporter.
# Copyright (C) 2024 Anamitra Ghorui

import subprocess
from pathlib import Path
from typing import Any, Dict
from .base import MAX_PROCESS_TIMEOUT, AbstractFileExporter, FileExporterOptionSet, FileExporterResponse


class Exporter(AbstractFileExporter):
	NAME = "svg"
	DESCRIPTION = "Exports an Inkscape SVG file to a plain SVG"
	PATTERNS = [ "*.svg" ]

	INKSCAPE_EXEC_NAME = "inkscape"
	DEFAULT_SUFFIX = ".svg"

	OPTIONS = FileExporterOptionSet(
		("suffix", str, "specify extension of the exported file", DEFAULT_SUFFIX)
	)

	def __init__(self, options: Dict[str, Any] = {}) -> None:
		super().__init__(options)

		self.suffix = options["suffix"] if "suffix" in options else self.DEFAULT_SUFFIX

	def export(self, src_path: Path, dest_path: Path, name: str) -> FileExporterResponse:
		dest_full_path = dest_path.joinpath(name).with_suffix(self.suffix)

		proc = subprocess.Popen(
			[
				self.INKSCAPE_EXEC_NAME,
				"--export-plain-svg",
				f"--export-filename={dest_full_path}",
				src_path
			],
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
			dest_path = dest_full_path,
		)