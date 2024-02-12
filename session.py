from async_list import AsyncList
from packet import Packet


class Session:

    on_end_of_session = None

    def __init__(self, first_packet: Packet):
        self._first_packet = first_packet
        self._session_id = self._first_packet.session_id
        self._source_id = self._first_packet.source_id
        self._packet_queue = AsyncList()
        self._timestamp_increment, self._audio_length_ms = self._first_packet.payload_details()

    @property
    def id(self) -> str:
        return f"{self.source_id:04X}:{self.session_id:04X}"

    @property
    def source_id(self) -> int:
        return self._source_id

    @property
    def session_id(self) -> int:
        return self._session_id

    async def on_packet(self, packet: Packet):
        async with self._packet_queue:
            self._packet_queue.append(packet)
