import asyncio
import time

from poly_packet import PolyPacket
from session import Session


class PolySession(Session):

    def __init__(self, first_packet: PolyPacket):
        super().__init__(first_packet)
        self.__first_packet = first_packet

        self.__prev_audio = None

    def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.__send_page())

    async def __send_page(self):
        # send alert packets
        await self.__first_packet.send_poly_alert_packets()

        print(f"Session {self.id} streaming started")
        # the poly phones are very sensitive to the timestamps on the audio packets
        # so recreate the timestamps to avoid problems (core dumps on the phone!)
        timestamp = 0
        # send transmit packets at regular intervals
        # record time at start of audio stream
        start_ms = self.__get_time_ms()
        # print(start_ms)
        transmit_packet = 0
        while True:
            async with self._packet_queue:
                # we are 1 second behind the imcoming stream
                # so when we run out of data the stream has ended
                if not any(self._packet_queue):
                    break
                packet = self._packet_queue.pop(0)
            # print(str(packet))

            # transmit this audio packet
            await packet.send_poly_transmit_packet(self.__prev_audio, timestamp)
            # save the audio for the next audio packet
            self.__prev_audio = bytes(packet.audio)

            # advance the timetamp
            timestamp += self._timestamp_increment

            # sleep until the time for the next audio packet
            now_ms = self.__get_time_ms()
            # print(now_ms)
            transmit_packet += 1
            sleep_ms = start_ms + transmit_packet * self._audio_length_ms - now_ms
            # wait for the time to send the next packet
            # always at least yield to let other stuff run
            await asyncio.sleep(max(0.001, sleep_ms / 1000.0))

            # continue sending audio packets

        print(f"Session {self.id} streaming complete")

        # timeout of stream then end packets
        await asyncio.sleep(0.050)

        # send end packets after 50ms of no transmit packets
        await self.__first_packet.send_poly_end_packets()

        await self.on_end_of_session(self)

    @staticmethod
    def __get_time_ms() -> float:
        return time.monotonic() * 1000.0
