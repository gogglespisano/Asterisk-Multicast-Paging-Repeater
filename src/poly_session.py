import asyncio
import time

from poly_packet import PolyPacket
from session import Session

_packet_pre_sleep_ms = 2


class PolySession(Session):

    def __init__(self, first_packet: PolyPacket):
        super().__init__(__name__, first_packet)
        self.__first_packet = first_packet

        self.__prev_audio = None

    def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.__send_page())

    async def __send_page(self):
        # send alert packets
        await self.__first_packet.send_poly_alert_packets()

        self.log.info(f"Session {self.id} streaming started")
        # the poly phones are very sensitive to the timestamps on the audio packets
        # so recreate the timestamps to avoid problems (core dumps on the phone!)
        timestamp = 0
        start_ms = 0.0
        self.log.debug(f"Session starting timestamp: {start_ms}")
        packet_number = 0
        while True:
            async with self._packet_queue:
                # we are 1 second behind the imcoming stream
                # so when we run out of data the stream has ended
                if not any(self._packet_queue):
                    break
                packet = self._packet_queue.pop(0)
            self.log.debug(f"Sending packet: {packet}")

            # sleep until the time for the next audio packet
            now_ms = self.__get_time_ms()
            # align the timing of the first packet
            if packet_number == 0:
                # record time at start of audio stream
                # always based timing off of the start time so that we don't accumulate error
                start_ms = now_ms
            # first do an async sleep to get close to the time
            sleep_ms = start_ms + ((packet_number * self._audio_length_ms) - _packet_pre_sleep_ms) - now_ms
            # wait for the time close to sending the next packet
            if sleep_ms > 0.1:
                await asyncio.sleep(sleep_ms / 1000.0)

            now_ms = self.__get_time_ms()
            # wait (blocking) for the last bit of time before sending the packer
            sleep_ms = start_ms + (packet_number * self._audio_length_ms) - now_ms
            # wait for the time to send the next packet
            if sleep_ms > 0.1:
                time.sleep(sleep_ms / 1000.0)

            # transmit this audio packet
            packet.send_poly_transmit_packet(self.__prev_audio, timestamp)
            # save the audio for the next audio packet
            self.__prev_audio = bytes(packet.audio)

            # advance the timetamp and packet number
            timestamp += self._timestamp_increment
            packet_number += 1

            # continue sending audio packets

        self.log.info(f"Session {self.id} streaming complete")

        # timeout of stream then end packets
        await asyncio.sleep(0.050)

        # send end packets after 50ms of no transmit packets
        await self.__first_packet.send_poly_end_packets()

        await self.on_end_of_session(self)

    @staticmethod
    def __get_time_ms() -> float:
        return time.monotonic() * 1000.0
