# define Python user-defined exceptions
class NoAvailableStudentSlots(Exception):
    """Raised when the program cant find more student slots available"""
    pass


class MissingHarnessEnvVars(Exception):
    """Raised when the program cant find the required environment variables"""
    pass


class VaultConnFailure(Exception):
    """Raised when the program fails to connect to Vault"""
    pass


class VaultQueryFailure(Exception):
    """Raised when the program fails to query Vault for secrets"""
    pass
