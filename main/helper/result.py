class Result:

    success = None
    message = None
    data = None

    def __init__(self):
        self.success = False
        self.message = ''

    def set_success(self, success):
        self.success = success

    def set_data(self, data):
        self.data = data

    def set_message(self, message):
        self.message = message

    def get_success(self):
        return self.success

    def get_message(self):
        return self.message

    def get_data(self):
        return self.data

    def __str__(self):
        return 'Success: ' + str(self.success) + ', Data: ' + str(self.data) + ', Message: ' + str(self.message)
