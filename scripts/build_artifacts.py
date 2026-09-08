#!/usr/bin/env python3
"""Rebuild displays from archived evidence, public reports and explicit designs."""
import runpy
from pathlib import Path
P=Path(__file__).resolve().parent
for name in ['build_benchmark_tables.py','build_research_tables.py','build_figures.py']:
    runpy.run_path(str(P/name),run_name='__main__')
print('Built benchmark tables, controlled-study tables and serif vector figures.')
