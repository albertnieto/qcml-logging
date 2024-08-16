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
Context Filter Module

This module contains the ContextFilter class, which is used to add contextual
information to log records.
"""

import logging

class ContextFilter(logging.Filter):
    """
    A logging filter that adds contextual information to log records.

    Attributes:
        context_info (dict): Contextual information to be added to each log record.
    """

    def __init__(self, context_info):
        """
        Initialize the ContextFilter.

        Args:
            context_info (dict): Contextual information to be added to log records.
        """
        super().__init__()
        self.context_info = context_info

    def filter(self, record):
        """
        Add context information to the log record.

        Args:
            record (logging.LogRecord): The log record to be modified.

        Returns:
            bool: True to indicate that the record should be logged.
        """
        for key, value in self.context_info.items():
            setattr(record, key, value)
        return True
