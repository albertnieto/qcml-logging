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
Handlers Module

This module contains custom log handlers, including the SlackHandler
for sending log messages to Slack.
"""

import logging
from logging.handlers import RotatingFileHandler
import os

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    slack_available = True
except ImportError:
    slack_available = False

class SlackHandler(logging.Handler):
    """
    A logging handler that sends log messages to a Slack channel.

    Attributes:
        slack_client (WebClient): Slack WebClient to send messages.
        channel (str): Slack channel where messages will be posted.
    """

    def __init__(self, slack_client, channel):
        """
        Initialize the SlackHandler.

        Args:
            slack_client (WebClient): Initialized Slack WebClient.
            channel (str): Slack channel where messages will be posted.
        """
        super().__init__(level=logging.INFO)
        self.slack_client = slack_client
        self.channel = channel

    def emit(self, record):
        """
        Send the log record to the configured Slack channel.

        Args:
            record (logging.LogRecord): The log record to be sent.
        """
        log_entry = self.format(record)
        try:
            self.slack_client.chat_postMessage(channel=self.channel, text=f"```{log_entry}```")
        except SlackApiError as e:
            logging.error(f"Failed to send log to Slack: {e.response['error']}")

def setup_handlers(output, logs_path, log_filename, max_bytes, backup_count, level, formatter):
    """
    Set up logging handlers based on user configuration.

    Args:
        output (str): Output destination ('terminal', 'file', 'both').
        logs_path (str): Path where log files are stored.
        log_filename (str): Name of the log file.
        max_bytes (int): Maximum size of log file before rotation.
        backup_count (int): Number of backup files to keep.
        level (int): Logging level.
        formatter (logging.Formatter): Formatter for the logs.

    Returns:
        list: List of configured handlers.
    """
    handlers = []

    if output in ("terminal", "both"):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        handlers.append(stream_handler)

    if output in ("file", "both"):
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
        file_handler = RotatingFileHandler(os.path.join(logs_path, log_filename), maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    return handlers

def setup_slack_handler(slack_credentials):
    """
    Set up a Slack logging handler if Slack credentials are provided.

    Args:
        slack_credentials (list): Slack API token and channel.

    Returns:
        SlackHandler: Configured SlackHandler instance.

    Raises:
        ValueError: If Slack credentials are invalid.
        SlackApiError: If Slack authentication fails.
    """
    if not slack_credentials or len(slack_credentials) != 2:
        raise ValueError("Slack credentials must be a list containing the token and channel.")
    slack_token, slack_channel = slack_credentials
    slack_client = WebClient(token=slack_token)
    
    # Check Slack connection
    try:
        response = slack_client.auth_test()
        if not response['ok']:
            raise SlackApiError("Slack authentication failed", response)
    except SlackApiError as e:
        logging.error(f"Failed to authenticate Slack: {e.response['error']}")
        raise

    return SlackHandler(slack_client, slack_channel)
