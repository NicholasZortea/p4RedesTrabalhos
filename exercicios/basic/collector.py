from scapy.all import *
import struct
import time
import os

class Collector:
    def process(self, pkt):
        # apenas IPv4
        if IP in pkt:
            raw_bytes = bytes(pkt)
            telemetry_offset = 14 + 20

            packet_counter, bytes_counter, queue_time, jitter = struct.unpack(
                "!IIII",
                raw_bytes[telemetry_offset:telemetry_offset + 16]
            )
            self.printValues(packet_counter, bytes_counter, queue_time, jitter)

    def printValues(self, packet, byte, queue_time, jitter):
        os.system('clear')
        print("==== TELEMETRIA ====")
        print("Pacotes:", packet)
        print("Bytes:", byte)
        print("Queue time:", queue_time)
        print("Jitter:", jitter)
        print()
        
collector = Collector()
def process(pkt):
    collector.process(pkt)

sniff(iface="eth0", prn=process)

