from asyncio import DatagramProtocol

from log import Log


class Protocol(Log, DatagramProtocol):
    def __init__(self, log_name: str):
        super().__init__(log_name)
        self._transport = None

    def connection_lost(self, exc):
        self.log.exception("Connection Lost: %s", exc, exc_info=True)

    def error_received(self, exc):
        self.log.exception("Error Receieved: %s", exc, exc_info=True)
