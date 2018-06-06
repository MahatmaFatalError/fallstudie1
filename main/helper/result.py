

class Result:

    success = None
    message = ''

    def __init__(self):
        self.success = False
        self.message = ''

    def set_success(self, success):
        self.success = success

    def set_message(self, message):
        self.message = message

    def get_success(self):
        return self.success

    def get_message(self):
        return self.message

    def __str__(self):
        return 'Success: ' + str(self.success) + ', Message: ' + self.message
