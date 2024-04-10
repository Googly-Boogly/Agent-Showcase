"""
This is a universal Page to be used across projects
"""
import logging
import os
import traceback
import inspect
import time
from typing import Optional, Callable, Any

import yaml
# Optional Imports:
# These 3 for the database connection
import pymysql.cursors
# from dotenv import load_dotenv
#
# load_dotenv()


def log_exceptions(file_prefix: Optional[str] = None):
    """
        Logs and exceptions that occur in the function
        To use:
        from helpful_functions import log_exceptions
        @log_exceptions
        def some_function(*args, *kwargs):
    """

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            calling_frame = inspect.stack()[1]
            file_path: str = calling_frame[1]
            file_name: str = func.__name__

            if file_prefix is not None:
                file_name = file_prefix + file_name

            personal_logger2 = PersonalLogger(file_path, file_name)
            py_logger_object: logging.Logger = personal_logger2.create_logger_error()

            result: Optional[Any] = None
            try:
                result = func(*args, **kwargs)
            except CustomError as custom_error:
                personal_logger2.log_it(custom_error)
                raise custom_error
            except Exception as e:
                personal_logger2.log_it(e)
                raise e
            finally:
                return result

        return wrapper

    return decorator


def benchmark_function(file_prefix: Optional[str] = None):
    """
    Benchmarks your function, and creates a benchmark log file
    :param file_prefix: if you want to add a suffix to the function name
    :return:
    To use:
        from helpful_functions import benchmark_logs
        @benchmark_logs
        def some_function(**args, **kwargs):
    """

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            calling_frame = inspect.stack()[1]
            file_path: str = calling_frame[1]
            file_name: str = func.__name__

            if file_prefix is not None:
                file_name = file_prefix + file_name

            personal_logger2 = PersonalLogger(file_path, file_name)
            bm_logger: logging.Logger = personal_logger2.create_benchmark()
            start_time = time.time()

            result: Any = func(*args, **kwargs)

            end_time_section1 = time.time()
            time_section1 = end_time_section1 - start_time
            bm_logger.debug(f"{file_name} took {time_section1} seconds")
            return result

        return wrapper

    return decorator


def benchmark_and_log_exceptions(file_prefix: Optional[str] = None):
    """
        Benchmarks your function
        To use: from helpful_functions import benchmark_and_log_exceptions
        @benchmark_and_log_exceptions
        def some_function(**args, **kwargs):
    """

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            calling_frame = inspect.stack()[1]
            file_path: str = calling_frame[1]
            file_name: str = func.__name__

            if file_prefix is not None:
                file_name = file_prefix + file_name

            personal_logger2 = PersonalLogger(file_path, file_name)
            bm_logger: logging.Logger = personal_logger2.create_benchmark()

            personal_logger_object = PersonalLogger(file_path, file_name)
            logger2: logging.Logger = personal_logger_object.create_logger_error()

            result: Optional[Any] = None

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
            except CustomError as custom_error:
                personal_logger2.log_it(custom_error)
                raise
            except Exception as e:
                personal_logger2.log_it(e)
            finally:
                end_time_section1 = time.time()
                time_section1 = end_time_section1 - start_time
                bm_logger.debug(f"{file_name} took {time_section1} seconds")
                return result

        return wrapper

    return decorator


class PersonalLogger:
    """
    really shitty logger class
    """

    def __init__(self, file_path: str, name_of_function: str):
        self.file_path = file_path
        self.name_of_function = name_of_function
        self.py_logger_object: logging.Logger = logging.getLogger()

    def log_it(self, error: Exception):
        """
        Takes in logger and error and logs the error and the line number it occured on
        :param error: the error that occured
        :return: None
        """
        log_message = f"An exception occurred on line {traceback.extract_tb(error.__traceback__)[-1].lineno}: {error}"
        self.py_logger_object.error(log_message)

    def create_benchmark(self) -> logging.Logger:
        """
        Creates a logger object that will log the time it takes to run a function
        Creates it in the same folder as the calling function
        is fully DEBUG LEVEL LOGGER
        :return:
        """
        caller_dir = os.path.dirname(os.path.abspath(self.file_path))

        logs_dir = os.path.join(caller_dir, 'logs')

        os.makedirs(logs_dir, exist_ok=True)

        # Create a subfolder named after the calling file (without extension)
        calling_file_name = os.path.splitext(os.path.basename(self.file_path))[0]
        file_logs_dir = os.path.join(logs_dir, calling_file_name)

        os.makedirs(file_logs_dir, exist_ok=True)
        log_file = os.path.join(file_logs_dir, f'BM_{self.name_of_function}.log')

        logger = logging.getLogger(self.name_of_function)

        # Create a file handler and set the formatter
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Set the logging level to capture all levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger.setLevel(logging.DEBUG)

        # Add the file handler to the logger
        logger.addHandler(handler)
        # Logs to console!!!!!
        # logger.addHandler(console_handler)
        self.py_logger_object = logger
        return logger

    def create_debugger(self):
        pass

    def create_logger_error(self):
        """
        To use the logger
        from global_code.helpful_functions import create_logger_error, log_it
        import traceback
        logger = create_logger_error(os.path.abspath(__file__), '')
        try:
            x = 0/0
        except Exception as e:
            log_it(logger, e)
        """

        caller_dir = os.path.dirname(os.path.abspath(self.file_path))

        logs_dir = os.path.join(caller_dir, 'logs')

        os.makedirs(logs_dir, exist_ok=True)

        # Create a subfolder named after the calling file (without extension)
        calling_file_name = os.path.splitext(os.path.basename(self.file_path))[0]
        file_logs_dir = os.path.join(logs_dir, calling_file_name)

        os.makedirs(file_logs_dir, exist_ok=True)
        log_file = os.path.join(file_logs_dir, f'{self.name_of_function}.log')

        logger = logging.getLogger(self.name_of_function)

        # Create a file handler and set the formatter
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Set the logging level to capture all levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger.setLevel(logging.DEBUG)

        # Add the file handler to the logger
        logger.addHandler(handler)
        logger.addHandler(console_handler)
        self.py_logger_object = logger

        return logger


class CustomError(Exception):
    """
        This is a custom error class, to be used in the log_exceptions decorator
        make this class more robust as needed
        when you raise this error, it will log the error
        Will let the error continue up through the stack
    """

    def __init__(self, message: str, error_type: str = None):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


# this class will give us an instance of a connection to our database
class MySQLConnection:
    """
    THIS WILL ONLY WORK IN A DOCKER CONTAINER, WITH ENVIRONMENT VARIABLES FOR MYSQL STUFF
    """

    def __init__(self, db, host: Optional[str] = None, port: Optional[int] = None
                 , user: Optional[str] = None, password: Optional[str] = None):
        # connection = pymysql.connect(
        #     host=host or os.getenv("MYSQL_HOST"),
        #     port=port or int(os.getenv("MYSQL_PORT")),
        #     user=user or os.getenv("MYSQL_USER"),
        #     password=password or os.getenv("MYSQL_PASSWORD"),
        #     charset='utf8mb4',
        #     cursorclass=pymysql.cursors.DictCursor,
        #     autocommit=True
        # )
        # with connection.cursor() as cur:
        #     cur.execute('CREATE DATABASE swarm_db;')
        connection = pymysql.connect(
            host=host or os.getenv("MYSQL_HOST"),
            port=port or int(os.getenv("MYSQL_PORT")),
            user=user or os.getenv("MYSQL_USER"),
            password=password or os.getenv("MYSQL_PASSWORD"),
            db=db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        self.connection = connection
        self.logger = create_logger_error(file_path=os.path.abspath(__file__), name_of_log_file='SQL_QUERY_LOGS',
                                     log_to_console=True, log_to_file=False)

    # the method to query the database
    def query_db(self, query, data=None) -> int or tuple or bool:
        with self.connection.cursor() as cursor:
            try:
                query = cursor.mogrify(query, data)
                # On off SQL Text buttton

                # log_it(logger=self.logger, error=None, custom_message=f"SQL QUERY: {query}", log_level="info")
                cursor.execute(query, data)
                if query.lower().find("insert") >= 0:
                    # INSERT queries will return the ID NUMBER of the row inserted
                    self.connection.commit()
                    return cursor.lastrowid
                elif query.lower().find("select") >= 0:
                    # SELECT queries will return the data from the database as a LIST OF DICTIONARIES
                    result = cursor.fetchall()
                    return result
                else:
                    # UPDATE and DELETE queries will return nothing
                    self.connection.commit()
            except Exception as e:
                log_it(logger=self.logger, error=e, log_level="error")
                return False
            # finally:
            #     self.connection.close()
            # connectToMySQL receives the database we're using and uses it to create an instance of MySQLConnection


class PostgreSQLConnection:
    """
    This class will work with environment variables for PostgreSQL configuration.
    Ensure that the following environment variables are set:
    - POSTGRES_HOST
    - POSTGRES_PORT
    - POSTGRES_DB
    - POSTGRES_USER
    - POSTGRES_PASSWORD
    """

    # import psycopg2
    def __init__(self, db: Optional[str], host: Optional[str] = None, port: Optional[int] = None,
                 user: Optional[str] = None, password: Optional[str] = None):
        raise NotImplemented
        # You can print out the environment variables to verify they're being read correctly
    #     print(os.getenv("POSTGRES_HOST"))
    #     connection = psycopg2.connect(
    #         dbname=db or os.getenv("POSTGRES_DB"),
    #         user=user or os.getenv("POSTGRES_USER"),
    #         password=password or os.getenv("POSTGRES_PASSWORD"),
    #         host=host or os.getenv("POSTGRES_HOST"),
    #         port=port or os.getenv("POSTGRES_PORT"),
    #     )
    #     connection.autocommit = True
    #     self.connection = connection
    #
    # def query_db(self, query, data=None) -> int or tuple or bool:
    #     with self.connection.cursor() as cursor:
    #         try:
    #             cursor.execute(query, data)
    #             if query.lower().find("insert") >= 0:
    #                 # INSERT queries will return the ID NUMBER of the row inserted
    #                 return cursor.fetchone()[0]  # Assuming RETURNING is used in INSERT
    #             elif query.lower().find("select") >= 0:
    #                 # SELECT queries will return the data from the database as a LIST OF DICTIONARIES
    #                 columns = [desc[0] for desc in cursor.description]
    #                 result = [dict(zip(columns, row)) for row in cursor.fetchall()]
    #                 return result
    #             else:
    #                 # For UPDATE and DELETE queries, you might want to return the number of rows affected
    #                 return cursor.rowcount
    #         except Exception as e:
    #             print(e)
    #             return False


def connect_to_db(db, db_type: str = "mysql") -> MySQLConnection or PostgreSQLConnection:
    """
    returns the object to interact with the DB
    :param db: name of the database inside the DB server
    :param db_type: types of DB you want to connect to
    :return: the class you want to use to interact with the DB
    """
    if db_type == "postgres":
        return PostgreSQLConnection(db)
    if db_type == "mysql":
        return MySQLConnection(db)


def count_lines_of_code(directory: str) -> int:
    """
    Needs to be the absolute path of the directory also will exclude the venv folder
    only counts .py files
    :param directory: Absolute path of the directory
    :return: Total_lines of python in project
    """

    total_lines = 0

    for root, dirs, files in os.walk(directory):
        if "venv" in dirs:
            dirs.remove("venv")

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    total_lines += len(lines)

    return total_lines


def create_logger_error(file_path: str, name_of_log_file: str, log_to_console: bool = False,
                        log_to_file: bool = False) -> logging.Logger:
    """
    Creates a logger object.
    When you call EX: logger.debug(), it will create a log in the same folder the calling function is. And create a log file
    this log file will be named whatever you want.
    WARNING: This function seems to only work using a synchronous function.
    It is breaking if you use it in async code.
    TODO: Fix potential problems with async code.
    :param log_to_file: True if you want to log to a file, False if you don't want to log to a file
    :param log_to_console: (bool) if you want to log to console. Default: Won't log to the console.
    :param file_path: (str) absolute path of the file, this code: os.path.abspath(__file__)
    :param name_of_log_file: (str) name of the log file.
    :return: the python logger object.
    Usage example:
    from helpful_functions import create_logger_error, log_it
    logger = create_logger_error(file_path=os.path.abspath(__file__), name_of_log_file='name',
                                 log_to_console=True, log_to_file=True)
    try:
        x = 0/0
    except Exception as e:
        log_it(logger, e)
    """
    logger = logging.getLogger(name_of_log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Sets the format of the console log and adds it if required
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_to_file:
        caller_dir = os.path.dirname(os.path.abspath(file_path))
        logs_dir = os.path.join(caller_dir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        # Create a subfolder named after the calling file (without extension)
        calling_file_name = os.path.splitext(os.path.basename(file_path))[0]
        file_logs_dir = os.path.join(logs_dir, calling_file_name)
        os.makedirs(file_logs_dir, exist_ok=True)

        log_file = os.path.join(file_logs_dir, f'{name_of_log_file}.log')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.setLevel(logging.DEBUG)

    return logger


def log_it(logger: logging.Logger, error: Optional[Exception] = None, custom_message: Optional[str] = None,
           log_level: Optional[str] = None) -> Optional[Exception]:
    """
    Takes in logger and error and logs the error in the correct way
    :param log_level: Has to be one of the following: debug, info, warning, error, critical
    :param custom_message: a custom message
    :param logger: logger object made in one of the logger maker functions
    :param error: the error that occurred, this code: except Exception as e:
    :return: the Exception that was passed in or nothing if it was None
    How to use:
    from helpful_functions import create_logger_error, log_it
    logger = create_logger_error(file_path=os.path.abspath(__file__), name_of_log_file='name',
                                 log_to_console=True, log_to_file=True)
    try:
        x = 0/0
    except Exception as e:
        log_it(logger, e)
        OR
        log_it(logger=logger, error=None, custom_message="This is a custom message", log_level="info")
    """
    if isinstance(error, Exception):
        log_message = f"An exception occurred on line {traceback.extract_tb(error.__traceback__)[-1].lineno}: {error}"
        if log_level is not None:
            if custom_message is not None:
                log_message_custom_message = log_message + '\n' + custom_message
                if log_level == "debug":
                    logger.debug(log_message_custom_message)
                elif log_level == "info":
                    logger.info(log_message_custom_message)
                elif log_level == "warning":
                    logger.warning(log_message_custom_message)
                elif log_level == "error":
                    logger.error(log_message_custom_message)
                elif log_level == "critical":
                    logger.critical(log_message_custom_message)
                else:
                    raise CustomError("type_of_log must be one of the following: debug, info, warning, error, critical")
            if log_level == "debug":
                logger.debug(log_message)
            elif log_level == "info":
                logger.info(log_message)
            elif log_level == "warning":
                logger.warning(log_message)
            elif log_level == "error":
                logger.error(log_message)
            elif log_level == "critical":
                logger.critical(log_message)
            else:
                raise CustomError("type_of_log must be one of the following: debug, info, warning, error, critical")

        logger.error(log_message)
    elif error is None:
        if custom_message is not None:
            if log_level is not None:
                if log_level == "debug":
                    logger.debug(custom_message)
                elif log_level == "info":
                    logger.info(custom_message)
                elif log_level == "warning":
                    logger.warning(custom_message)
                elif log_level == "error":
                    logger.error(custom_message)
                elif log_level == "critical":
                    logger.critical(custom_message)
                else:
                    raise CustomError("type_of_log must be one of the following: debug, info, warning, error, critical")
            else:
                logger.info(custom_message)
    return error


def create_logger_simple(file_name: str, name: str) -> logging.Logger:
    # ---------------------------------------------------------------------------
    # Older version of the logger maker
    # is broken
    # ---------------------------------------------------------------------------

    logger = logging.getLogger(name)

    caller_dir = os.path.dirname(os.path.abspath(file_name))  # this line is probably broken
    logs_dir = os.path.join(caller_dir, "../utils/logs")
    os.makedirs(logs_dir, exist_ok=True)  # Create the "logs" folder if it doesn't exist

    log_file = os.path.join(logs_dir, f"{name}.log")
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


def load_config(config_path: str = "config.yaml") -> dict[str, Any]:
    """
    :param config_path: config foler
    :return: the dict structure of the yaml file
    """
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
