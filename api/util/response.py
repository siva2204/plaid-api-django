def error_response(message):
    response = {
        "status_code": 400,
        "message": message,
    }

    return response


def unauthorized_response(message):
    response = {
        "status_code": 401,
        "message": message,
    }

    return response


def internalservererror_response():
    response = {
        "status_code": 500,
        'message': "internal server error, please try again later"
    }

    return response
