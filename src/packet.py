import socket
import struct

_payload_g726qi = 0xFD
_payload_g722 = 0x09
_payload_g711u = 0x00


class Packet:

    def __init__(self, data: bytes, addr: str):
        self._version = 0
        self._has_padding = False
        self._has_extension_header = False
        self._extension_header = None
        self._csrc_count = 0
        self._csrc_identifiers = None
        self._has_marker = False
        self._payload_type = 0
        self._sequence = 0
        self._timestamp = 0
        self._ssrc_identifier = 0
        self._audio = None

        self._source_id = struct.unpack("!L", socket.inet_aton(addr))[0]
        self.__decode_asterisk_packet(data)

    def __str__(self) -> str:
        return f"Seq: {self._sequence}, Time: {self._timestamp}, Audio: {self._audio[0:20]}..."

    @property
    def id(self) -> str:
        return f"{self.source_id:04X}:{self.session_id:04X}"

    @property
    def source_id(self) -> int:
        return self._source_id

    @property
    def session_id(self) -> int:
        return self._ssrc_identifier

    @property
    def audio(self) -> bytes:
        return self._audio

    def payload_details(self) -> (int, float):
        audio_data_length = len(self._audio)

        if self._payload_type == _payload_g711u:
            return audio_data_length, audio_data_length / 8.0
        elif self._payload_type == _payload_g722:
            return audio_data_length, audio_data_length / 8.0
        elif self._payload_type == _payload_g726qi:
            return (audio_data_length * 8) // 3, audio_data_length / 3.0
        else:
            raise Exception("Unsupported payload type")

    def __decode_asterisk_packet(self, data: bytes) -> None:
        data_length = len(data)

        # parse an RTP header
        if data_length < 12 + 1:
            raise Exception("Invalid multicast data")
        offset = 0
        byte0 = int.from_bytes(data[offset:offset + 1], "big")
        self._version = (byte0 >> 6) & 0x03
        if self._version != 2:
            raise Exception(f"RTP version {self._version} not supported")
        self._has_padding = (byte0 & 0x20) != 0
        self._has_extension_header = (byte0 & 0x10) != 0
        self._csrc_count = byte0 & 0x0F
        offset += 1
        byte1 = int.from_bytes(data[offset:offset + 1], "big")
        self._has_marker = (byte1 & 0x80) != 0
        self._payload_type = byte1 & 0x7F
        offset += 1
        self._sequence = int.from_bytes(data[offset:offset + 2], "big")
        offset += 2
        self._timestamp = int.from_bytes(data[offset:offset + 4], "big")
        offset += 4
        self._ssrc_identifier = int.from_bytes(data[offset:offset + 4], "big")
        offset += 4

        if self._csrc_count > 0:
            if data_length < offset + (self._csrc_count * 4):
                raise Exception("Invalid multicast data")
            self._csrc_identifiers = [int.from_bytes(data[offset + (x * 4):offset + (x * 4) + 4], "big") for x in range(self._csrc_count)]
            offset += (self._csrc_count * 4)

        if self._has_extension_header:
            if data_length < offset + 4:
                raise Exception("Invalid multicast data")
            self.__extension_header_id = int.from_bytes(data[offset:offset + 2], "big")
            offset += 2
            extension_header_length = int.from_bytes(data[offset:offset + 2], "big")
            offset += 2
            if extension_header_length > 0:
                if len(data) < offset + extension_header_length:
                    raise Exception("Invalid multicast data")
                self._extension_header = data[offset:offset + extension_header_length]
                offset += extension_header_length

        # the audio data is what follows the rtp header
        if data_length < offset + 1:
            raise Exception("Invalid multicast data")
        self._audio = data[offset:]
