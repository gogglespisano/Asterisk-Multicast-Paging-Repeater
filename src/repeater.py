import asyncio

from asterisk_protocol import AsteriskProtocol
from async_list import AsyncList
from config import Config
from log import Log
from poly_packet import PolyPacket
from poly_protocol import PolyProtocol
from poly_session import PolySession
from session import Session


class Repeater(Log):
    def __init__(self):
        super().__init__(__name__)
        self.__poly_transport = None
        self.__poly_protocol = None
        self.__asterisk_transport = None
        self.__asterisk_protocol = None

        self.__sessions = AsyncList()

        Config.the().validate()

    def start(self):
        self.log.info("Starting Multicast Paging Repeater")

        Session.on_end_of_session = self.on_end_of_session

        loop = asyncio.get_event_loop()
        loop.create_task(self.__run(loop))

    async def __run(self, loop):
        self.__poly_transport, Config.the().poly_protocol = await loop.create_datagram_endpoint(
            lambda: PolyProtocol(Config.the().poly_multicast_ttl),
            remote_addr=(Config.the().poly_multicast_address, Config.the().poly_multicast_port))

        PolyPacket.send_poly_data = self.__poly_transport.sendto

        self.__asterisk_transport, self.__asterisk_protocol = await loop.create_datagram_endpoint(
            lambda: AsteriskProtocol(self.on_recv_asterisk_data, Config.the().asterisk_multicast_address),
            local_addr=('0.0.0.0', Config.the().asterisk_multicast_port))

        while True:
            await asyncio.sleep(1.0)

    async def on_recv_asterisk_data(self, data: bytes, addr: (str, int)) -> None:
        try:
            packet = PolyPacket(data, addr[0])
            self.log.debug(f"Received packet: {packet}")

            # find the existing session or None if not found
            async with self.__sessions:
                session = next((x for x in self.__sessions if x.session_id == packet.session_id and x.source_id == packet.source_id), None)

            # create and start a new session if session not found
            if session is None:
                # create a poly session
                async with self.__sessions:
                    session = PolySession(packet)
                    self.__sessions.append(session)
                self.log.info(f"Session {session.id} begin")
                session.start()

            # add this packet to the session
            await session.on_packet(packet)

        except Exception as exc:
            # ignore bad incoming packets
            self.log.warning("Bad Packet: %s", exc, exc_info=True)

    async def on_end_of_session(self, session):
        # remove the session for the list
        async with self.__sessions:
            self.__sessions.remove(session)
        self.log.info(f"Session {session.id} end")
