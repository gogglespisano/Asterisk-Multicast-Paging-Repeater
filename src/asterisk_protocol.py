import asyncio
import socket
import struct

from protocol import Protocol


class AsteriskProtocol(Protocol):
    def __init__(self, on_recv_asterisk_data, multicast_address: str):
        super().__init__(__name__)
        self.__on_recv_asterisk_data = on_recv_asterisk_data
        self.__multicast_address = multicast_address

    def connection_made(self, transport):
        self._transport = transport
        sock = self._transport.get_extra_info('socket')
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        multicast_group = socket.inet_aton(self.__multicast_address)
        multicast_request = struct.pack('4sL', multicast_group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_request)

    def datagram_received(self, data, addr):
        asyncio.get_event_loop().create_task(self.__on_recv_asterisk_data(data, addr))
