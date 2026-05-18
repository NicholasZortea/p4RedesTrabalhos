from scapy.all import *
import struct

def process(pkt):

    # apenas IPv4
    if IP in pkt:

        raw_bytes = bytes(pkt)

        #
        # Ethernet = 14 bytes
        # IPv4 normalmente = 20 bytes
        #
        telemetry_offset = 14 + 20

        #
        # Lê:
        # packet_counter
        # bytes_counter
        #
        packet_counter, bytes_counter = struct.unpack(
            "!II",
            raw_bytes[telemetry_offset:telemetry_offset + 8]
        )

        print("==== TELEMETRIA ====")
        print("Pacotes:", packet_counter)
        print("Bytes:", bytes_counter)
        #print(raw_bytes)
        print()

sniff(iface="eth0", prn=process)