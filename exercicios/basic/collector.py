from scapy.all import *
import struct
import csv
import os

CSV_FILE = "telemetry.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "packets",
            "bytes",
            "queue_time",
            "jitter",
            "switch_id"
        ])

class Collector:
    def process(self, pkt):
        if IP in pkt:
            raw_bytes = bytes(pkt)
            telemetry_offset = 14 + 20

            packet_counter, bytes_counter, queue_time, jitter, switch_id = struct.unpack(
                "!IIIIB",
                raw_bytes[telemetry_offset:telemetry_offset + 17]
            )

            with open(CSV_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    packet_counter,
                    bytes_counter,
                    queue_time,
                    jitter,
                    switch_id
                ])

collector = Collector()

sniff(iface="eth0", prn=collector.process)