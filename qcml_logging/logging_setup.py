# Copyright 2024 Albert Nieto

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Logging Setup Module

This module provides the main setup function for configuring logging in various
environments, including support for terminal, file, and Slack logging.
"""

import logging
import sys
from .formatters import setup_formatter
from .handlers import setup_handlers, setup_slack_handler
from .context import ContextFilter

try:
    from slack_sdk.errors import SlackApiError
    slack_available = True
except ImportError:
    slack_available = False

def setup_logging_filters(logger, keyword_filters, context_info):
    """
    Set up logging filters based on keywords and context information.

    Args:
        logger (logging.Logger): Logger instance.
        keyword_filters (list): List of keywords to filter logs.
        context_info (dict): Context information to add to logs.
    """
    if keyword_filters:
        def filter_keywords(record):
            return any(keyword in record.msg for keyword in keyword_filters)
        keyword_filter = logging.Filter()
        keyword_filter.filter = filter_keywords
        logger.addFilter(keyword_filter)

    if context_info:
        context_filter = ContextFilter(context_info)
        logger.addFilter(context_filter)

def setup_async_logging(logger):
    """
    Set up asynchronous logging by handling uncaught exceptions.

    Args:
        logger (logging.Logger): Logger instance.
    """
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.excepthook = handle_exception

def log_setup(level="ERROR", hide_logs=None, output="both", logs_path="logs/",
              log_filename=None, max_bytes=1048576, backup_count=3, 
              terminal_level=None, file_level=None, 
              log_format=None, use_json=False, keyword_filters=None, 
              use_color=True, asynchronous=True, add_context=False, context_info=None,
              slack_notify=False, slack_credentials=None):
    """
    Set up logging with various options including terminal, file, and Slack logging.

    Args:
        level (str): Default logging level as a string (e.g., 'DEBUG', 'INFO').
        hide_logs (list): List of libraries whose logs should be hidden (set to ERROR level).
        output (str): Where to output logs. Options are 'terminal', 'file', or 'both'. Default is 'both'.
        logs_path (str): Directory path where log files should be saved. Default is 'logs/'.
        log_filename (str): Custom log file name. Default is None.
        max_bytes (int): Maximum file size in bytes before rotating. Default is 1MB.
        backup_count (int): Number of backup files to keep. Default is 3.
        terminal_level (str): Logging level for terminal output. Default is the 'level' parameter.
        file_level (str): Logging level for file output. Default is the 'level' parameter.
        log_format (str): Log message format. Default is None.
        use_json (bool): Whether to use JSON format for logs. Default is False.
        keyword_filters (list): List of keywords to filter logs. Only logs containing these keywords will be shown. Default is None.
        use_color (bool): Whether to use color-coded logs in the terminal. Default is True.
        asynchronous (bool): Whether to use asynchronous logging. Default is True.
        add_context (bool): Whether to add contextual information to logs. Default is False.
        context_info (dict): Contextual information to be added to logs. Default is None.
        slack_notify (bool): Whether to send notifications to Slack. Default is False.
        slack_credentials (list): Slack API token and channel as a list. Required if slack_notify is True.
    """
    
    # Default terminal and file levels to the main logging level
    terminal_level = terminal_level or level
    file_level = file_level or level

    # Setup logging levels
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper(), logging.ERROR))

    # Remove existing handlers
    logger.handlers.clear()

    # Setup formatter
    formatter = setup_formatter(use_json, use_color, log_format)

    # Setup and add handlers
    handlers = setup_handlers(output, logs_path, log_filename, max_bytes, backup_count, 
                              getattr(logging, terminal_level.upper(), logging.ERROR), 
                              formatter)
    
    for handler in handlers:
        logger.addHandler(handler)

    # Log whether Slack SDK is available
    if slack_notify and slack_available:
        try:
            slack_handler = setup_slack_handler(slack_credentials)
            slack_handler.setFormatter(formatter)
            logger.addHandler(slack_handler)
        except (ValueError, SlackApiError) as e:
            logger.error(f"Slack setup failed: {str(e)}")
    elif slack_notify and not slack_available:
        logger.warning("Slack notifications are enabled, but the Slack SDK is not installed. Please install it to use this feature.")

    # Set logging levels for specified libraries
    if hide_logs:
        for library in hide_logs:
            logging.getLogger(library).setLevel(logging.ERROR)
            logger.info(f"{library} logs are set to ERROR level.")

    # Setup filters and context
    setup_logging_filters(logger, keyword_filters, context_info if add_context else None)

    # Setup asynchronous logging
    if asynchronous:
        setup_async_logging(logger)

    logger.info("Logging is set up.")

if __name__ == "__main__":
    # Example context information
    context_info = {
        'user_id': 'example_user',
        'session_id': 'example_session'
    }

    # Example Slack credentials (use environment variables for real use cases)
    slack_token = "your-slack-token"  # Replace with your Slack API token
    slack_channel = "#example-channel"
    slack_credentials = [slack_token, slack_channel]

    # Run a basic logging setup as an example
    log_setup(
        level="DEBUG",
        output="both",
        logs_path="example_logs",
        use_json=False,
        keyword_filters=["example", "test"],
        use_color=True,
        asynchronous=True,
        add_context=True,
        context_info=context_info,
        slack_notify=False,  # Set to True to enable Slack notifications
        slack_credentials=slack_credentials
    )

    # Example logging messages
    logging.debug("This is a debug message.")
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.critical("This is a critical message.")
