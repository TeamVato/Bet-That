class BettingBaseException(Exception):
    """Base exception for betting-related errors"""

    pass


class BetCreationError(BettingBaseException):
    """Raised when bet creation fails"""

    pass


class BetValidationError(BettingBaseException):
    """Raised when bet validation fails"""

    pass


class BetNotFoundError(BettingBaseException):
    """Raised when requested bet is not found"""

    pass


class UnauthorizedBetActionError(BettingBaseException):
    """Raised when user is not authorized for bet action"""

    pass


class BetParticipationError(BettingBaseException):
    """Raised when bet participation fails"""

    pass


class BetResolutionError(BettingBaseException):
    """Raised when bet resolution fails"""

    pass
