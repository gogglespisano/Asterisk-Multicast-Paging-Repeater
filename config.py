class Config(object):

    __the = None

    def __init__(self):
        self.asterisk_multicast_address = '224.0.1.116'
        self.asterisk_multicast_port = 5001

        self.poly_multicast_address = '224.0.1.116'
        self.poly_multicast_port = 5002
        self.poly_multicast_ttl = 32

        self.poly_group = 26
        self.poly_sender_id = 'Asterisk'

    @classmethod
    def the(cls):
        if cls.__the is None:
            cls.__the = Config()
        return cls.__the

    def validate(self):
        if not (26 <= self.poly_group <= 50):
            raise Exception('Channel must be between 26 and 50')

        if len(self.poly_sender_id) > 13:
            raise Exception('Caller ID must be no more than 13 characters')
