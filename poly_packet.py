import asyncio

from config import Config
from packet import Packet


class PolyPacket(Packet):

    send_poly_data = None

    def __init__(self, data: bytes, addr: str):
        super().__init__(data, addr)

    async def send_poly_alert_packets(self) -> None:
        for _ in range(31):
            PolyPacket.send_poly_data(self.__encode_poly_packet(True, False))
            await asyncio.sleep(0.030)

    async def send_poly_transmit_packet(self, prev_audio: bytes, timestamp: int) -> None:
        PolyPacket.send_poly_data(self.__encode_poly_packet(False, False, prev_audio, timestamp))

    async def send_poly_end_packets(self) -> None:
        for _ in range(12):
            PolyPacket.send_poly_data(self.__encode_poly_packet(False, True))
            await asyncio.sleep(0.030)

    def __encode_poly_packet(self, alert: bool, end: bool, prev_audio: bytes = None, timestamp: int = 0) -> bytes:
        opcode = 0x0F if alert else 0xFF if end else 0x10

        # create the data with the header
        data = bytearray(1 + 1 + 4 + 1 + 13)
        data[0] = opcode
        data[1] = Config.the().poly_group
        data[2:6] = self._source_id.to_bytes(4, "big")
        data[6] = len(Config.the().poly_sender_id)
        data[7:20] = bytes(Config.the().poly_sender_id.ljust(13, '\0'), 'ascii')

        # add audio to transmit packets
        if not alert and not end:
            data.extend(self._payload_type.to_bytes(1, "big"))
            data.extend(b'\0')
            data.extend(timestamp.to_bytes(4, "big"))

            # if the previous packet audio is supplied, insert it here
            if prev_audio is not None:
                data.extend(prev_audio)

            # add the packet audio
            data.extend(self._audio)

        return data
