import email
from xml.dom import ValidationErr
from django.core.validators import validate_email as _validate_email


def validate_email(email):
    try:
        _validate_email(email)
        return True
    except ValidationErr:
        return False
