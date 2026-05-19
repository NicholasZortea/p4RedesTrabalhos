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

            packet_counter, bytes_counter, queue_time = struct.unpack(
                "!III",
                raw_bytes[telemetry_offset:telemetry_offset + 12]
            )
            self.printValues(packet_counter, bytes_counter, queue_time)

    def printValues(self, packet, byte, queue_time):
        os.system('clear')
        print("==== TELEMETRIA ====")
        print("Pacotes:", packet)
        print("Bytes:", byte)
        print("Queue time:", queue_time)
        print()
        
collector = Collector()
def process(pkt):
    collector.process(pkt)


sniff(iface="eth0", prn=process)

