from scapy.all import *
import struct
import time
import os

class Collector:
    def __init__(self):
        self.last_print = 0

    def process(self, pkt):
        # apenas IPv4
        if IP in pkt:
            raw_bytes = bytes(pkt)
            telemetry_offset = 14 + 20

            packet_counter, bytes_counter = struct.unpack(
                "!II",
                raw_bytes[telemetry_offset:telemetry_offset + 8]
            )
            self.printValues(packet_counter, bytes_counter)

    def printValues(self, packet, byte):
        now = time.time()
        if now - self.last_print >= 3:
            os.system('clear')
            print("==== TELEMETRIA ====")
            print("Pacotes:", packet)
            print("Bytes:", byte)
            print()
            self.last_print = now

collector = Collector()
def process(pkt):
    collector.process(pkt)


sniff(iface="eth0", prn=process)

