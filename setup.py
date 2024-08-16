from setuptools import setup, find_packages

setup(
    name="qcml-logging",
    version="0.1.0",
    author="Albert Nieto",
    author_email="nietom.albert@gmail.com",
    description="A Python library for advanced logging with support for multiple outputs and optional Slack integration.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/albertnieto/qcml-logging",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "slack": ["slack_sdk>=3.0.0"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
