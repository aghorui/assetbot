# exporters.copy - Verbatim copy exporter.
# Copyright (C) 2024 Anamitra Ghorui

import shutil
from pathlib import Path
from typing import Any, Dict, List
from .base import AbstractFileExporter, FileExporterResponse


class Exporter(AbstractFileExporter):
	NAME: str = "copy"
	DESCRIPTION: str = "Produces a verbatim copy of the file to the destination location."
	PATTERNS: List[str] = []

	def __init__(self, options: Dict[str, Any] = {}) -> None:
		super().__init__(options)

	def export(self, src_path: Path, dest_path: Path, name: str) -> FileExporterResponse:
		final_dest = shutil.copy2(src_path, dest_path)
		return FileExporterResponse(dest_path = final_dest)

