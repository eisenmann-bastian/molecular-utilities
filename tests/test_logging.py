import io
import logging
import tempfile
import unittest
from pathlib import Path

from molecule_utilities.logging import configure_logging, get_logger


class LoggingTests(unittest.TestCase):
    def setUp(self):
        self.saved = {}
        for name in ("quick_qm", "test_logging_alpha", "test_logging_beta", "test_logging_parent",
                     "test_logging_parent.child"):
            logger = logging.getLogger(name)
            self.saved[name] = (logger.handlers[:], logger.level, logger.propagate)
            logger.handlers = []
            logger.setLevel(logging.NOTSET)
            logger.propagate = True
        self.addCleanup(self.restore)

    def restore(self):
        for name, (handlers, level, propagate) in self.saved.items():
            logger = logging.getLogger(name)
            for handler in logger.handlers:
                if handler not in handlers:
                    handler.close()
            logger.handlers = handlers
            logger.setLevel(level)
            logger.propagate = propagate

    def test_existing_defaults_and_idempotence(self):
        stream = io.StringIO()
        configure_logging(stream=stream)
        configure_logging(stream=stream)
        get_logger("test").info("message")
        self.assertEqual(stream.getvalue(), "INFO quick_qm.test: message\n")

    def test_namespaces_format_level_and_reconfiguration(self):
        first, second, other = io.StringIO(), io.StringIO(), io.StringIO()
        configure_logging(logging.DEBUG, first, namespace="test_logging_alpha",
                          format="%(levelname)s %(message)s")
        configure_logging(stream=other, namespace="test_logging_beta")
        alpha = get_logger("worker", namespace="test_logging_alpha")
        beta = get_logger("worker", namespace="test_logging_beta")
        alpha.debug("initial")
        configure_logging("WARNING", second, namespace="test_logging_alpha",
                          format="%(asctime)s %(message)s", datefmt="%Y", propagate=False)
        alpha.info("hidden")
        alpha.warning("updated")
        beta.info("separate")
        self.assertEqual(first.getvalue(), "DEBUG initial\n")
        self.assertRegex(second.getvalue(), r"^\d{4} updated\n$")
        self.assertEqual(other.getvalue(), "INFO test_logging_beta.worker: separate\n")
        self.assertEqual(len(logging.getLogger("test_logging_alpha").handlers), 1)

    def test_file_append_remove_and_preserve_unmanaged_handler(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "application.log"
            path.write_text("existing\n", encoding="utf-8")
            stream, external_stream = io.StringIO(), io.StringIO()
            external = logging.StreamHandler(external_stream)
            logger = logging.getLogger("test_logging_alpha")
            logger.addHandler(external)
            configure_logging(stream=stream, namespace="test_logging_alpha", file=path,
                              format="%(message)s")
            get_logger("worker", namespace="test_logging_alpha").info("first")
            configure_logging(stream=stream, namespace="test_logging_alpha", format="%(message)s")
            get_logger("worker", namespace="test_logging_alpha").info("second")
            self.assertEqual(path.read_text(encoding="utf-8"), "existing\nfirst\n")
            self.assertEqual(stream.getvalue(), "first\nsecond\n")
            self.assertEqual(external_stream.getvalue(), "first\nsecond\n")
            self.assertIn(external, logger.handlers)

    def test_parent_propagation_is_opt_in(self):
        parent_stream, child_stream = io.StringIO(), io.StringIO()
        configure_logging(stream=parent_stream, namespace="test_logging_parent", format="%(message)s")
        configure_logging(stream=child_stream, namespace="test_logging_parent.child",
                          format="%(message)s", propagate=True)
        get_logger("worker", namespace="test_logging_parent.child").warning("once")
        self.assertEqual(parent_stream.getvalue(), "once\n")
        self.assertEqual(child_stream.getvalue(), "once\n")

    def test_invalid_configuration_leaves_previous_logging_intact(self):
        stream = io.StringIO()
        configure_logging(stream=stream, namespace="test_logging_alpha")
        for options in ({"level": "INVALID"}, {"format": "%(bad"}, {"propagate": 1},
                        {"file": ""}, {"file": Path("/definitely-missing-dir/file.log")}):
            with self.subTest(options=options), self.assertRaises((ValueError, TypeError, OSError)):
                configure_logging(namespace="test_logging_alpha", **options)
        get_logger("worker", namespace="test_logging_alpha").warning("still active")
        self.assertIn("still active", stream.getvalue())

    def test_invalid_logger_names_are_rejected(self):
        for namespace in ("", " root", "root.", ".root", "root..child", None):
            with self.subTest(namespace=namespace), self.assertRaises(ValueError):
                configure_logging(namespace=namespace)
        for name in ("", " worker", "a..b", None):
            with self.subTest(name=name), self.assertRaises(ValueError):
                get_logger(name)


if __name__ == "__main__":
    unittest.main()
