# SheetManager Exceptions
class InitSheetManagerError(Exception):
    pass


class AuthSheetManagerError(Exception):
    pass


class CheckinError(Exception):
    pass


# Holdings Exceptions
class HoldingsQueryException(Exception):
    pass


class BadBibstemException(Exception):
    pass


#Tasks Exceptions
class DBCommitException(Exception):
    """Non-recoverable Error with making database commits."""
    pass


class DBReadException(Exception):
    """Non-recoverable Error with making database selection."""
    pass


#Utils Exceptions
class ReadBibstemException(Exception):
    pass


class ReadCanonicalException(Exception):
    pass


class ReadEncodingException(Exception):
    pass


class RequestsException(Exception):
    pass


class ReadRefsourcesException(Exception):
    pass
