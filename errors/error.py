class CineTrakerError(Exception):
    pass

class TraktAuthError(CineTrakerError):
    pass

class TokenRequestError(CineTrakerError):
    pass

class ApiRequestError(CineTrakerError):
    pass

class EmptyList(CineTrakerError):
    pass