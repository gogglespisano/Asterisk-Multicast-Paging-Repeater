import socket
import struct
from asyncio import DatagramProtocol


class PolyProtocol(DatagramProtocol):
    def __init__(self, multicast_ttl):
        self.__multicast_ttl = multicast_ttl
        self.__transport = None

    def connection_made(self, transport):
        self.__transport = transport
        sock = self.__transport.get_extra_info('socket')
        multicast_ttl = struct.pack('@i', self.__multicast_ttl)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, multicast_ttl)
        # try a couple of different methods to set the don't fragment bit
        try:
            # IP_MTU_DISCOVER, IP_PMTUDISC_DO
            sock.setsockopt(socket.IPPROTO_IP, 10, 2)
        except Exception as ex:
            print("Warning: IP_MTU_DISCOVER, IP_PMTUDISC_DO", ex)
        try:
            # IP_DONTFRAG
            sock.setsockopt(socket.IPPROTO_IP, 14, 1)
        except Exception as ex:
            print("Warning: IP_DONTFRAG", ex)

    def connection_lost(self, ex):
        print(ex)

    def datagram_received(self, data, addr):
        # poly receive data (phone outgoing page)  ignored
        pass

    def error_received(self, ex):
        print(ex)
