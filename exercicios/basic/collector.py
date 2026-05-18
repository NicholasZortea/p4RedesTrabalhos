from scapy.all import sniff

def process(pkt):
    print(pkt.summary())

sniff(iface="eth0", prn=process)