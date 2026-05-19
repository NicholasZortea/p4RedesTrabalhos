from scapy.all import *
import time

iface = "h1-eth0"

macs = {
    "10.0.1.1": "08:00:00:00:01:11",
    "10.0.2.2": "08:00:00:00:02:22",
    "10.0.4.4": "08:00:00:00:04:44",
    "10.0.5.5": "08:00:00:00:05:55",
    "10.0.6.6": "08:00:00:00:06:66",
}

hosts = list(macs.keys())

payload_size = 100
step = 100
max_size = 2000
i = 0

while True:
    dst_ip = hosts[i % len(hosts)]
    dst_mac = macs[dst_ip]

    payload = "X" * payload_size

    pkt = Ether(dst=dst_mac, src=get_if_hwaddr(iface)) / \
          IP(dst=dst_ip) / \
          ICMP() / \
          payload

    sendp(pkt, iface=iface, verbose=False)

    print(f"Sent to {dst_ip} | MAC={dst_mac} | size={payload_size}")

    payload_size += step
    if payload_size > max_size:
        payload_size = 100

    i += 1
    time.sleep(0.2)