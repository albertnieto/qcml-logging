# QCML Logging Library

QCML Logging is a Python library that provides advanced logging setup with support for multiple outputs (terminal, file) and Slack integration. It includes features like color-coded logs, JSON formatting, and contextual information.

## Installation

You can install the library using pip:

```bash
pip install qcml-logging
```

## Usage

Here’s an example of how to set up logging:

```python
import qcml_logging

context_info = {
    'user_id': '12345',
    'session_id': 'abcde'
}

slack_credentials = ["your-slack-token", "#your-channel"]

qcml_logging.log_setup(
    level="DEBUG",
    output="both",
    logs_path="my_logs",
    use_json=False,
    keyword_filters=["error", "critical"],
    use_color=True,
    asynchronous=True,
    add_context=True,
    context_info=context_info,
    slack_notify=True,
    slack_credentials=slack_credentials
)

logging.debug("This is a debug message.")
```