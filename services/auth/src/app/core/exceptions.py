class AuthError(Exception):
    """Base execption for service"""


class UserAlreadyExistsError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass


class TokenValidationError(AuthError):
    pass


class UserNotFoundError(AuthError):
    pass
