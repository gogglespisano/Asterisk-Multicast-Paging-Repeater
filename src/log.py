import logging


class Log:
    def __init__(self, log_name: str = __name__):
        self.log = logging.getLogger(log_name)

    @staticmethod
    def setup():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-17s %(levelname)-9s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
