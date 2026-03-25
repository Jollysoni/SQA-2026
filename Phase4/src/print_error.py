"""print_error.py

Defines the shared ErrorLogger utility used across all Back End modules.

The format intentionally matches the course starter code style so fatal file-format
problems and non-fatal transaction-processing problems are easy to see.
"""

import sys


class ErrorLogger:
    """Prints formatted error messages and can terminate the program for fatal errors."""

    @staticmethod
    def log(description, context, fatal=False):
        """Print an error in the required course format and optionally stop the program.

        Args:
            description: human-readable explanation of what went wrong
            context:     file name or operation where the error occurred
            fatal:       if True, prints a fatal-error message and exits with status 1
        """
        if fatal:
            print(f"ERROR: Fatal error - File {context} - {description}")
            sys.exit(1)
        print(f"ERROR: {context}: {description}")