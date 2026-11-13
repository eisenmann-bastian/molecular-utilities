"""Demonstrate an application-specific shared logger."""

from molecular_utilities.logging import configure_logging, get_logger


def main():
    configure_logging(namespace="logging_example")
    logger = get_logger("example", namespace="logging_example")
    logger.info("Shared logging is configured")


if __name__ == "__main__":
    main()
