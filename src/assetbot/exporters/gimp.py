# exporters.gimp - GIMP XCF to png exporter.
# Copyright (C) 2024 Anamitra Ghorui

import re
import subprocess
from pathlib import Path
from typing import Any, Dict
from .base import MAX_PROCESS_TIMEOUT, AbstractFileExporter, FileExporterOptionSet, FileExporterResponse


class Exporter(AbstractFileExporter):
	NAME = "gimp"
	DESCRIPTION = "Exports a GIMP XCF file to PNG"
	PATTERNS = [ "*.xcf" ]

	GIMP_EXEC_NAME = "gimp"
	DEFAULT_SUFFIX = ".png"

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
				self.GIMP_EXEC_NAME,
				"--no-interface",
				"-b",
				f"""
				(let* ( (inputfile "{re.escape(str(src_path))}" ) (outputfile "{re.escape(str(dest_full_path))}") (image 0) (layer 0) )
					(set! image (car (gimp-file-load RUN-NONINTERACTIVE inputfile inputfile)))
					(set! layer (car (gimp-image-merge-visible-layers image CLIP-TO-IMAGE)))
					(gimp-file-save RUN-NONINTERACTIVE image layer outputfile outputfile)
					(gimp-image-delete image)
					(gimp-quit 0)
				)
				"""
			],
			stdin  = None,
			stdout = subprocess.PIPE,
			stderr = subprocess.STDOUT
		)

		output_log = proc.communicate(timeout = MAX_PROCESS_TIMEOUT)[0]
		if proc.stdin != None:
			proc.stdin.close()

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