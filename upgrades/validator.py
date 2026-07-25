"""
CopySwift AI Validator
Version: 3.0.0
"""

from pathlib import Path


class Validator:

    @staticmethod
    def file_exists(path):
        return Path(path).exists()

    @staticmethod
    def is_python_file(path):
        return str(path).endswith(".py")

    @staticmethod
    def validate_patch(path):
        if not Validator.file_exists(path):
            return False, "Patch file does not exist."

        if not Validator.is_python_file(path):
            return False, "Invalid patch file."

        return True, "Patch validation successful."


if __name__ == "__main__":

    print("=" * 50)
    print("CopySwift AI Validator")
    print("=" * 50)

    status, message = Validator.validate_patch(__file__)

    print("Status :", status)
    print("Message:", message)
