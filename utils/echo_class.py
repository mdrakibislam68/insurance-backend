class Echo:
    """An object that implements just the write method of the file-like interface.
    This is used to stream the CSV data.
    """

    def write(self, value):
        return value
