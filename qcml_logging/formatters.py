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
Formatters Module

This module contains custom log formatters, including the ColoredFormatter
for color-coded log output.
"""

import logging
import json

DEFAULT_JSON_FORMAT = json.dumps({
    'time': '%(asctime)s',
    'name': '%(name)s',
    'level': '%(levelname)s',
    'message': '%(message)s',
    'filename': '%(filename)s',
    'line': '%(lineno)d'
})

class ColoredFormatter(logging.Formatter):
    """
    A logging formatter that adds color to log messages based on their severity.

    Attributes:
        COLORS (dict): Mapping of log levels to terminal color codes.
        RESET (str): Terminal code to reset color.
    """
    COLORS = {
        'DEBUG': '\033[92m',  # Green
        'INFO': '\033[94m',   # Blue
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[95m' # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        """
        Format the specified log record as text.

        Args:
            record (logging.LogRecord): The log record to be formatted.

        Returns:
            str: The formatted log record string.
        """
        colored_levelname = f"{self.COLORS.get(record.levelname, self.RESET)}{record.levelname}{self.RESET}"
        record.levelname = colored_levelname
        return super().format(record)

def setup_formatter(use_json, use_color, log_format):
    """
    Set up the logging formatter based on the user's preferences.

    Args:
        use_json (bool): Whether to format logs as JSON.
        use_color (bool): Whether to use color-coded logs.
        log_format (str): Custom log format.

    Returns:
        logging.Formatter: Configured formatter instance.
    """
    if use_json:
        return logging.Formatter(fmt=DEFAULT_JSON_FORMAT)
    elif use_color:
        return ColoredFormatter(log_format)
    else:
        return logging.Formatter(log_format)
