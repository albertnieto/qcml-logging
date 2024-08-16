import unittest
import logging
import os
import sys
from qcml_logging.logging_setup import log_setup
from qcml_logging.handlers import SlackHandler

class TestLoggingSetup(unittest.TestCase):

    def setUp(self):
        """Set up test environment before each test."""
        # Set up paths and filenames for tests
        self.logs_path = "test_logs"
        self.log_filename = "test.log"
        
        # Ensure logs directory is clean before each test
        if os.path.exists(self.logs_path):
            for file in os.listdir(self.logs_path):
                file_path = os.path.join(self.logs_path, file)
                os.unlink(file_path)
        else:
            os.makedirs(self.logs_path)

    def tearDown(self):
        """Clean up test environment after each test."""
        if os.path.exists(self.logs_path):
            for file in os.listdir(self.logs_path):
                file_path = os.path.join(self.logs_path, file)
                os.unlink(file_path)
            os.rmdir(self.logs_path)

    def test_terminal_logging(self):
        """Test that logging to the terminal works correctly."""
        log_setup(level="DEBUG", output="terminal")
        logger = logging.getLogger()

        with self.assertLogs(logger, level="DEBUG") as log:
            logger.debug("Test terminal log")
            self.assertIn("Test terminal log", log.output[0])

    def test_file_logging(self):
        """Test that logging to a file works correctly."""
        log_setup(level="DEBUG", output="file", logs_path=self.logs_path, log_filename=self.log_filename)
        logger = logging.getLogger()

        logger.debug("Test file log")

        log_file_path = os.path.join(self.logs_path, self.log_filename)
        self.assertTrue(os.path.exists(log_file_path))

        with open(log_file_path, 'r') as f:
            logs = f.read()
            self.assertIn("Test file log", logs)

    def test_both_logging(self):
        """Test that logging to both terminal and file works correctly."""
        log_setup(level="DEBUG", output="both", logs_path=self.logs_path, log_filename=self.log_filename)
        logger = logging.getLogger()

        with self.assertLogs(logger, level="DEBUG") as log:
            logger.debug("Test both log")

            # Check terminal output
            self.assertIn("Test both log", log.output[0])

            # Check file output
            log_file_path = os.path.join(self.logs_path, self.log_filename)
            self.assertTrue(os.path.exists(log_file_path))

            with open(log_file_path, 'r') as f:
                logs = f.read()
                self.assertIn("Test both log", logs)

    def test_logging_with_context(self):
        """Test that logging with context information works correctly."""
        context_info = {'user_id': '12345', 'session_id': 'abcde'}
        log_setup(level="DEBUG", output="terminal", add_context=True, context_info=context_info)
        logger = logging.getLogger()

        with self.assertLogs(logger, level="DEBUG") as log:
            logger.debug("Test context log")
            self.assertIn("Test context log", log.output[0])
            self.assertIn("user_id=12345", log.output[0])
            self.assertIn("session_id=abcde", log.output[0])

    def test_slack_handler_initialization(self):
        """Test that the SlackHandler can be initialized (without sending a real message)."""
        # Assuming slack_sdk is installed and available
        try:
            from slack_sdk import WebClient
            slack_client = WebClient(token="dummy_token")
            slack_handler = SlackHandler(slack_client, "#dummy-channel")
            self.assertIsInstance(slack_handler, SlackHandler)
        except ImportError:
            self.skipTest("slack_sdk is not installed; skipping SlackHandler test.")

    def test_logging_levels(self):
        """Test that logging levels are set correctly."""
        log_setup(level="WARNING", output="terminal")
        logger = logging.getLogger()

        with self.assertLogs(logger, level="WARNING") as log:
            logger.warning("This is a warning")
            self.assertIn("This is a warning", log.output[0])

        with self.assertRaises(AssertionError):
            with self.assertLogs(logger, level="WARNING"):
                logger.info("This info should not be logged")

    def test_log_rotation(self):
        """Test that log rotation works correctly."""
        small_max_bytes = 50  # Use a small size to force rotation quickly
        log_setup(level="DEBUG", output="file", logs_path=self.logs_path, log_filename=self.log_filename, max_bytes=small_max_bytes, backup_count=1)
        logger = logging.getLogger()

        # Write enough logs to trigger rotation
        for i in range(10):
            logger.debug(f"Log entry {i}")

        log_files = os.listdir(self.logs_path)
        self.assertTrue(len(log_files) > 1)  # Should have more than one file due to rotation

    def test_async_logging(self):
        """Test that asynchronous logging setup works without crashing."""
        log_setup(level="ERROR", output="terminal", asynchronous=True)
        logger = logging.getLogger()

        try:
            raise ValueError("This is a test exception")
        except ValueError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

        with self.assertLogs(logger, level="CRITICAL") as log:
            logger.critical("This is a critical error")
            self.assertIn("This is a critical error", log.output[0])

if __name__ == "__main__":
    unittest.main()
