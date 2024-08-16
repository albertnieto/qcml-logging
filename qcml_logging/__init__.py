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
QCML Logging Library

This is the main package for the QCML logging library. It provides an easy-to-use
interface for setting up advanced logging with support for multiple outputs, formats,
and integration with Slack.
"""

from .context import ContextFilter
from .formatters import setup_formatter, ColoredFormatter
from .handlers import setup_handlers, setup_slack_handler, SlackHandler
from .logging_setup import log_setup, setup_logging_filters, setup_async_logging

__all__ = [
    'ContextFilter',
    'setup_formatter',
    'ColoredFormatter',
    'setup_handlers',
    'setup_slack_handler',
    'SlackHandler',
    'log_setup',
    'setup_logging_filters',
    'setup_async_logging'
]
