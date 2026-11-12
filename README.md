# Molecular utilities

Shared Python utilities for molecular tools. Currently provides
`molecule_utilities.logging.configure_logging` and `get_logger`.

## Logging

Configure logging once at the application entry point, then obtain child
loggers using the same namespace:

```python
import logging
from molecule_utilities.logging import configure_logging, get_logger

configure_logging(
    namespace="my_project",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    file="my-project.log",
)
logger = get_logger("worker", namespace="my_project")
logger.info("Started")
```

`namespace` isolates each application's loggers. `level` accepts Python logging
levels or names. `format` and `datefmt` follow the standard `logging` formatter.
`stream` selects a console stream (default: standard error); `file` optionally
adds a UTF-8 file handler in append mode. The console remains enabled when a
file is specified. `propagate` controls forwarding to parent loggers and
defaults to `False`. When enabled, ensure parent handlers do not unintentionally
duplicate messages.

Calling `configure_logging` again for the same namespace **replaces the
utility-managed handlers and applies all supplied settings**. Omitted options
reset to their defaults; in particular, omitting `file` removes a previously
configured file handler. Other handlers remain untouched. Changing a stream
does not close the old stream. A configuration error is raised without
replacing the existing configuration.

Existing calls without a namespace continue to use `quick_qm`, level `INFO`,
and the format `%(levelname)s %(name)s: %(message)s`. To avoid overlapping
handlers across projects, use distinct, non-nested namespaces unless parent
propagation is intentional.

## Development

For local development, install with `python -m pip install -e .`.
Run tests with `python -m unittest discover -s tests`.
