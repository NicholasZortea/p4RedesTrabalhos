// SPDX-License-Identifier: Apache-2.0
/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<32> PKT_INSTANCE_TYPE_INGRESS_CLONE = 1;

/*************************************************************************
*********************** H E A D E R S  ***********************************
* This program skeleton defines minimal Ethernet and IPv4 headers and    *
* a simple LPM (Longest-Prefix Match) IPv4 forwarding pipeline.          *
* The exercise intentionally leaves TODOs for learners to implement.     *
*************************************************************************/

typedef bit<9>  egressSpec_t;   // Standard BMv2 uses 9 bits for egress_spec
typedef bit<48> macAddr_t;      // Ethernet MAC address
typedef bit<32> ip4Addr_t;      // IPv4 address

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}
const bit<32> HOST3_IP = 0x0A000303;

struct metadata {
    @field_list(1)
    bit<32> pkt_count;
    @field_list(1)
    bit<32> byte_count;
}

header telemetry {
    bit<32> packet_counter;
    bit<32> bytes_counter;
    bit<32> queue_time;
    bit<32> jitter;
    bit<8> switch_id;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    telemetry    telemetry;
}

/*************************************************************************
*********************** P A R S E R  *************************************
* New to P4? A typical parser does this:
*   start -> parse_ethernet
*   parse_ethernet:
*       if etherType == TYPE_IPV4 -> parse_ipv4
*       else accept
*   parse_ipv4 -> accept
* This skeleton leaves the actual states as a TODO to implement later.   *
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
          TYPE_IPV4: parse_ipv_4;
          default: accept;
        }
    }
    state parse_ipv_4 {
      packet.extract(hdr.ipv4);
      transition accept;
    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
* High-level intent:
*   - Do an LPM lookup on IPv4 dstAddr
*   - On hit, call ipv4_forward(next-hop MAC, output port)
*   - Otherwise, drop or NoAction (as configured)                         *
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    
    register<bit<32>>(10) window_bytes;
    register<bit<32>>(1) window_index;
    register<bit<32>>(1) window_sum;
    register<bit<32>>(1) amount_of_packets_to_clone;
    register<bit<32>>(1) clone_counter;

    register<bit<32>>(1) packet_counter_reg;
    register<bit<32>>(1) byte_counter_reg;
    

    bit<32> pkt_count;
    bit<32> clone_pkt;
    bit<32> byte_count;

    bit<32> threshold;
    bit<32> idx;
    bit<32> sum;

    action drop() {
        mark_to_drop(standard_metadata);
    }

   action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
        hdr.ethernet.dstAddr = dstAddr;
        if(hdr.ipv4.dstAddr==HOST3_IP && standard_metadata.instance_type != PKT_INSTANCE_TYPE_INGRESS_CLONE) {
            drop();
        }
    }

table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    action clone_packet() {
        clone_preserving_field_list(CloneType.I2E, 100, 1);
    }

    apply {
        if (hdr.ipv4.isValid()) {
            packet_counter_reg.read(pkt_count, 0);
            pkt_count = pkt_count + 1;
            packet_counter_reg.write(0, pkt_count);

            byte_counter_reg.read(byte_count, 0);
            byte_count = byte_count + (bit<32>) hdr.ipv4.totalLen;
            byte_counter_reg.write(0, byte_count);
            
            meta.pkt_count = pkt_count;
            meta.byte_count = byte_count;
            
            clone_counter.read(clone_pkt, 0);
            clone_pkt = clone_pkt + 1;

            amount_of_packets_to_clone.read(threshold, 0);
            window_index.read(idx, 0);
            window_sum.read(sum, 0);

            bit<32> old_value;
            window_bytes.read(old_value, idx);

            sum = sum - old_value;
            if(sum < 0) {
                sum = 0;
            }

            bit<32> pkt_size;
            pkt_size = (bit<32>) hdr.ipv4.totalLen;

            sum = sum + pkt_size;

            window_bytes.write(idx, pkt_size);

            idx = (idx + 1);
            if (idx >= 10) {
                idx = 0;
            }
            window_index.write(0, idx);

            window_sum.write(0, sum);

            if(sum < 1000) {
                threshold = 10;
            } else if (sum > 1000 && sum < 1500) {
                threshold = 5;
            } else {
                threshold = 3;
            }
            amount_of_packets_to_clone.write(0, threshold);

            if(clone_pkt >= threshold) {
                clone_packet();
                clone_pkt = 0;
            }
            clone_counter.write(0, clone_pkt);

            ipv4_lpm.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
* Often used for queue marks, mirroring, or post-routing edits.          *
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    register<bit<32>>(1) last_queue_time_reg;
    register<bit<8>>(1) switch_id_reg;
    bit<32> previous_queue_time;
    bit<32> queue_time;
    bit<32> jitter;
    bit<8> switch_id;

    apply { 
        if(standard_metadata.instance_type == PKT_INSTANCE_TYPE_INGRESS_CLONE) {
            hdr.telemetry.setValid();
            hdr.telemetry.packet_counter = meta.pkt_count;
            hdr.telemetry.bytes_counter = meta.byte_count;
            hdr.telemetry.queue_time = standard_metadata.deq_timedelta;
            switch_id_reg.read(switch_id, 0);
            hdr.telemetry.switch_id = switch_id;
            queue_time = standard_metadata.deq_timedelta;
            last_queue_time_reg.read(previous_queue_time, 0);
            if(queue_time < previous_queue_time) {
                jitter = previous_queue_time - queue_time;
            } else {
                jitter = queue_time - previous_queue_time;
            }
            last_queue_time_reg.write(0, queue_time);
            hdr.telemetry.jitter = jitter;
            hdr.ipv4.dstAddr = HOST3_IP;
    }
    }
}

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
        update_checksum(
            hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}


/*************************************************************************
***********************  D E P A R S E R  *******************************
* The deparser serializes headers back onto the packet in order.         *
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        /*
        Typical implementation (left as a TODO for learners):
            packet.emit(hdr.ethernet);
            packet.emit(hdr.ipv4);   // per P4_16 spec, emit appends a header
                                     // only if it is valid; no 'if' needed.
        */
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.telemetry);
    }
}

/*************************************************************************
***********************  S W I T C H  ***********************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
