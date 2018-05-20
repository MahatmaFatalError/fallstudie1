import sys


class SignalHandler:

    stopper = None
    threads = None

    def __init__(self, stopper, threads):
        self.stopper = stopper
        self.threads = threads

    def __call__(self, signum, frame):
        self.stopper.set()

        for thread in self.threads:
            thread.join()
        sys.exit(0)