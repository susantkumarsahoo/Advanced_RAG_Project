import sys
import traceback
from datetime import datetime


class CustomException(Exception):
    """
    Enterprise-grade custom exception for ML/AI pipelines.
    Provides detailed traceback, timestamp, and structured logs.
    """

    def __init__(self, error_message: Exception, error_details):
        super().__init__(str(error_message))
        self.error_message = self.get_detailed_error_message(
            error_message,
            error_details
        )

    @staticmethod
    def get_detailed_error_message(error_message: Exception, error_details) -> str:
        _, _, exc_tb = error_details.exc_info()

        if exc_tb is None:
            return f"Error: {str(error_message)} (No traceback available)"

        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno

        full_traceback = traceback.format_exc()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return (
            "\n" + "=" * 70 +
            f"\nTimestamp     : {timestamp}"
            f"\nFile Name     : {file_name}"
            f"\nLine Number   : {line_number}"
            f"\nError Message : {str(error_message)}"
            f"\nTraceback     :\n{full_traceback}"
            + "=" * 70 + "\n"
        )

    def __str__(self):
        return self.error_message


# useage    
'''
try:
    x = undefined_variable
except Exception as e:
    raise CustomException(e, sys)
'''