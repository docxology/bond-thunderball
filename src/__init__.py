"""Thunderball source package root.

This directory is a Python package container for the ``thunderball`` BOND
film package (see :mod:`thunderball`). ``thunderball`` resolves through the
editable install (``uv sync --extra dev``) or through pytest's ``pythonpath``
setting; nothing here manipulates ``sys.path``. It intentionally contains no
business logic.
"""
