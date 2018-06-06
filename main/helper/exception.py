class YelpError(Exception):
    """Base class for other exceptions"""

    def __init__(self, code, description):
        self.code = code
        self.description = description

    def __str__(self):
        return repr(self.code + '-' + self.description)
