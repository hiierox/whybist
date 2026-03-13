class KinopoiskApiError(Exception):
    status_code = 502


class KinopoiskUnauthorizedError(KinopoiskApiError):
    status_code = 401


class KinopoiskLimitExceededError(KinopoiskApiError):
    status_code = 402


class KinopoiskNotFoundError(KinopoiskApiError):
    status_code = 404


class KinopoiskRateLimitError(KinopoiskApiError):
    status_code = 429


class KinopoiskTransportError(KinopoiskApiError):
    status_code = 503


class KinopoiskInvalidResponseError(KinopoiskApiError):
    status_code = 502
