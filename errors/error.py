class CineTrakerError(Exception):
    pass

class TraktAuthError(CineTrakerError):
    pass

class TokenRequestError(CineTrakerError):
    pass

class ApiRequestError(CineTrakerError):
    pass

class ApiRequestProfileError(CineTrakerError):
    pass

class EmptyList(CineTrakerError):
    pass

class PostersError(CineTrakerError):
    pass


class ErrorFetchImage(CineTrakerError):
    pass

class ListNotFoundError(CineTrakerError):
    pass