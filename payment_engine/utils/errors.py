def error_response(code, message, details=None):
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        }
    }

    if details is not None:
        response["error"]["details"] = details

    return response
