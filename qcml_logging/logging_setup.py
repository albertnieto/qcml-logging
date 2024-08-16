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
import os
import sys
from typing import Optional, List, Dict

try:
    from slack_sdk.errors import SlackApiError
    slack_available = True
except ImportError:
    slack_available = False

# Handle imports correctly depending on how the module is executed
if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from formatters import setup_formatter
    from handlers import setup_handlers, setup_slack_handler
    from context import ContextFilter
else:
    from .formatters import setup_formatter
    from .handlers import setup_handlers, setup_slack_handler
    from .context import ContextFilter

def setup_logging_filters(logger: logging.Logger, keyword_filters: Optional[List[str]], context_info: Optional[Dict[str, str]]):
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

def setup_async_logging(logger: logging.Logger):
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

def log_setup(level: str = "ERROR", 
              hide_logs: Optional[List[str]] = None, 
              output: str = "both", 
              logs_path: str = "logs/",
              log_filename: Optional[str] = None, 
              max_bytes: int = 1048576, 
              backup_count: int = 3, 
              terminal_level: Optional[str] = None, 
              file_level: Optional[str] = None, 
              log_format: Optional[str] = None, 
              use_json: bool = False, 
              keyword_filters: Optional[List[str]] = None, 
              use_color: bool = True, 
              asynchronous: bool = True, 
              add_context: bool = False, 
              context_info: Optional[Dict[str, str]] = None,
              slack_notify: bool = False, 
              slack_credentials: Optional[List[str]] = None):
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
    
    # Safety checks
    if output not in {"terminal", "file", "both"}:
        raise ValueError(f"Invalid output value: {output}. Must be 'terminal', 'file', or 'both'.")
    
    if slack_notify and slack_credentials is None:
        raise ValueError("Slack notifications are enabled, but no Slack credentials were provided.")
    
    if output in {"file", "both"} and log_filename is None:
        log_filename = "default.log"
        logging.warning("No log filename provided. Defaulting to 'default.log'.")

    if not isinstance(max_bytes, int) or max_bytes <= 0:
        raise ValueError("max_bytes must be a positive integer.")

    if not isinstance(backup_count, int) or backup_count < 0:
        raise ValueError("backup_count must be a non-negative integer.")

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

    def inspect_logger(logger):
        print(f"Logger Name: {logger.name}")
        print(f"Logger Level: {logging.getLevelName(logger.level)}")
        print("Handlers:")
        for handler in logger.handlers:
            print(f"  - {type(handler).__name__} at {logging.getLevelName(handler.level)} level")
            if isinstance(handler, logging.StreamHandler):
                print("  - This is a StreamHandler (for terminal output).")
            elif isinstance(handler, logging.FileHandler):
                print("  - This is a FileHandler (for file output).")
            # Explicitly flush the handler to ensure logs are written
            handler.flush()

    # Example context information
    context_info = {
        'user_id': 'example_user',
        'session_id': 'example_session'
    }

    log_setup(
        level="DEBUG",
        output="both",
        file_level="DEBUG",
        terminal_level="DEBUG",
        logs_path="example_logs",
        log_filename="default.log",  # Explicitly setting the log file name
        use_json=False,
        keyword_filters=["example", "test"],
        use_color=True,
        asynchronous=True,
        add_context=True,
        context_info=context_info,
        slack_notify=False
    )

    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Explicitly set to DEBUG level
    logger.propagate = False  # Disable propagation to avoid interference

    # Inspect the logger configuration
    inspect_logger(logger)

    # Example logging messages
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

    # Ensure all handlers flush their buffers
    for handler in logger.handlers:
        handler.flush()

    print("Logging complete. Check the terminal and log file.")
