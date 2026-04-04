"""
Utility functions for logging and configuration.
"""
import logging
import os
import traceback
from typing import Optional, Callable, Any

import yaml


def load_config(config_path: str = "config.yaml") -> dict[str, Any]:
    """
    :param config_path: config file path
    :return: the dict structure of the yaml file
    """
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


class CustomError(Exception):
    """
    Custom error class for use with the log_exceptions decorator.
    When raised, it will be logged and continue up the stack.
    """

    def __init__(self, message: str, error_type: str = None):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


def log_exceptions(file_prefix: Optional[str] = None):
    """
    Decorator that logs any exceptions that occur in the decorated function.

    Usage:
        @log_exceptions()
        def some_function(*args, **kwargs):
            ...
    """

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            personal_logger = PersonalLogger(func.__name__)
            result: Optional[Any] = None
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                personal_logger.log_it(e)
                raise
            return result

        return wrapper

    return decorator


class PersonalLogger:
    """Simple logger that creates dated log files."""

    def __init__(self, name: str):
        self.name = name
        self.py_logger_object: logging.Logger = logging.getLogger(name)

    def log_it(self, error: Exception):
        """Log an exception with line number."""
        log_message = f"An exception occurred on line {traceback.extract_tb(error.__traceback__)[-1].lineno}: {error}"
        self.py_logger_object.error(log_message)


def create_logger_error(file_path: str, name_of_log_file: str, log_to_console: bool = False,
                        log_to_file: bool = False) -> logging.Logger:
    """
    Creates a logger object that logs to file and/or console.

    Usage:
        logger = create_logger_error(file_path=os.path.abspath(__file__), name_of_log_file='name',
                                     log_to_console=True, log_to_file=True)
    """
    logger = logging.getLogger(name_of_log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_to_file:
        caller_dir = os.path.dirname(os.path.abspath(file_path))
        logs_dir = os.path.join(caller_dir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        calling_file_name = os.path.splitext(os.path.basename(file_path))[0]
        file_logs_dir = os.path.join(logs_dir, calling_file_name)
        os.makedirs(file_logs_dir, exist_ok=True)

        log_file = os.path.join(file_logs_dir, f'{name_of_log_file}.log')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.DEBUG)
    return logger


def log_it(logger: logging.Logger, error: Optional[Exception] = None, custom_message: Optional[str] = None,
           log_level: Optional[str] = None) -> Optional[Exception]:
    """
    Log an error or custom message at the specified level.

    Usage:
        log_it(logger, error=e)
        log_it(logger, custom_message="Something happened", log_level="info")
    """
    level_map = {
        "debug": logger.debug,
        "info": logger.info,
        "warning": logger.warning,
        "error": logger.error,
        "critical": logger.critical,
    }

    if isinstance(error, Exception):
        log_message = f"An exception occurred on line {traceback.extract_tb(error.__traceback__)[-1].lineno}: {error}"
        if custom_message:
            log_message = f"{log_message}\n{custom_message}"
        log_fn = level_map.get(log_level, logger.error)
        log_fn(log_message)
    elif custom_message:
        log_fn = level_map.get(log_level, logger.info)
        log_fn(custom_message)

    return error
