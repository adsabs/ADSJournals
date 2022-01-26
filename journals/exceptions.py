# SheetManager Exceptions
class GoogleConnectionException(Exception):
    pass


class InitSheetManagerException(Exception):
    pass


class AuthSheetManagerException(Exception):
    pass


class CreateSheetException(Exception):
    pass


class LoadSheetException(Exception):
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


class InvalidTableException(Exception):
    pass


class TableCheckinException(Exception):
    pass


class TableCheckoutException(Exception):
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
