# Project instructions

- This package implements shared utilities; do not add a dependency on itself.
  Keep logging configuration opt-in, namespaced, and free of import-time side
  effects, preserving documented handler and reconfiguration behavior.
- Update tests and the [README](README.md) for public API changes. Run
  `python -m unittest discover -s tests -v` in an installed environment.
- Keep examples safe to run and do not overwrite existing environments.
