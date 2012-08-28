#! /usr/bin/env python
"""
Example to sniff all HTTP traffic on eth0 interface:
    sudo ./sniff.py eth0 "port 80"
"""
import os
import psycopg2
import re
import sys
import pcap
import string
import time
import socket
import struct
import binascii
import threading


from OSC import OSCClient, OSCMessage


protocols={socket.IPPROTO_TCP:'tcp',
            socket.IPPROTO_UDP:'udp',
            socket.IPPROTO_ICMP:'icmp'}
rows = []
known_sites = []



def send_count_to_chuck():
    global begin
    global count
    global start
    while ( start ):
        time_now = time.sleep(0.4)
        if time.time() - 0.8 > begin:
            print count
            send_count_via_osc_to_chuck(count )
            begin = time.time()
            count = 0


def send_count_via_osc_to_chuck(count):
    message = OSCMessage("/count")
    message.append(count)
    client.send(message)

def decode_ip_packet(pktlen, data, timestamp):
    global begin
    global count
    if not data:
        return
    else :
        s = data[14:]
        d = {}
        if len(s) > 6:
            d['version']=(ord(s[0]) & 0xf0) >> 4
            d['header_len']=ord(s[0]) & 0x0f
            d['tos']=ord(s[1])
            d['total_len']=socket.ntohs(struct.unpack('H',s[2:4])[0])
            d['id']=socket.ntohs(struct.unpack('H',s[4:6])[0])
            d['flags']=(ord(s[6]) & 0xe0) >> 5
            d['fragment_offset']=socket.ntohs(struct.unpack('H',s[6:8])[0] & 0x1f)
            d['ttl']=ord(s[8])
            d['protocol']=ord(s[9])
            d['checksum']=socket.ntohs(struct.unpack('H',s[10:12])[0])
            d['source_address']=pcap.ntoa(struct.unpack('i',s[12:16])[0])
            d['destination_address']=pcap.ntoa(struct.unpack('i',s[16:20])[0])
            if d['header_len']>5:
                d['options']=s[20:4*(d['header_len']-5)]
            else:
                d['options'] = None
                d['data'] = s[4*d['header_len']:]
                sport =  map(lambda x: '%.2x' % x, map(ord, d['data'][0:2]))
                dport = map(lambda x: '%.2x' % x, map(ord, d['data'][2:4]))
                d['sport'] = hex2dec(sport[0])*256 + hex2dec(sport[1])
                d['dport'] =  hex2dec(dport[0])*256 + hex2dec(dport[1])
                decode_protocole(d)
                if d['total_len']<300 and d['total_len']>0:
                    count = count +1

        return d

def decode_protocole(d):
    if is_dns_request(d):
        speak_daniel_speak(d)
    elif is_dhcp_request(d):
        launch_connection_sound()

def is_dhcp_request(d):
    return d['protocol'] == 17 and d['dport'] == 68


def launch_connection_sound():
    message = OSCMessage("/connection")
    client.send(message)


def is_dns_request(d):
    return d['protocol'] == 17 and d['dport'] == 53

def speak_daniel_speak(d):
    name_site = binascii.rledecode_hqx(d['data'][20:62])
    m = re.findall('\w+', name_site)
    if site_is_unknown(m[len(m)-2]):
        add_site_to_known_sites(m[len(m)-2])
        command_final = "say " +  m[len(m)-2] + " &"
        print (command_final)
        os.system(command_final)

def site_is_unknown(site):
    for i in xrange(0, len(known_sites)):
        if known_sites[i]== site:
            return False
    return True

def add_site_to_known_sites(site):
    if len(known_sites)>10:
        known_sites.pop(0)
    known_sites.append(site)

def send_message_to_chuck(d, address):
    message = OSCMessage("/chuck")
    message.append( (float(d['total_len'])/100))
    message.append (float(d['ttl']))
    param = find_from_num_ip(ip_to_numerical_address( address ))
    message.append (param)
    client.send(message)

def ip_to_numerical_address(ip_address):
    bytes = map(lambda x: '%.2x' % x, map(ord, ip_address))
    num_ip = 16777216*hex2dec(bytes[0]) + 65536*hex2dec(bytes[1]) + 256*hex2dec(bytes[2]) + hex2dec(bytes[3])
    return num_ip

def find_from_num_ip(num_address):
    max_value = len(rows)
    id_temp = max_value/2
    min_value = 0
    #k=0
    while  1 :
        if id_temp >= len(rows)-1:
            return rows[len(rows)-1][1]
        elif num_address < rows[id_temp][0]:
            max_value = id_temp
            id_temp = (id_temp + min_value)/2
            #k= k + 1
        elif num_address > rows[id_temp+1][0]:
            min_value = id_temp
            id_temp = (id_temp + max_value)/2
            #k = k + 1
        else:
            #print k
            return rows[id_temp][1]

def hex2dec(s):
    return int(s, 16)

def dumphex(s):
    bytes = map(lambda x: '%.2x' % x, map(ord, s))
    i=0
    for i in xrange(0,len(bytes)/16):
        print '        %s' % string.join(bytes[i*16:(i+1)*16],' ')
    print '        %s' % string.join(bytes[(i+1)*16:],' ')


def print_packet(pktlen, data, timestamp):
    if not data:
        return

    if data[12:14]=='\x08\x00':
        decoded = decode_ip_packet(pktlen, data, timestamp)
        print '\n%s.%f %s > %s' % (time.strftime('%H:%M',
                                time.localtime(timestamp)),
                                timestamp % 60,
                                decoded['source_address'],
                                decoded['destination_address'])
        for key in ['version', 'header_len', 'tos', 'total_len', 'id',
                                'flags', 'fragment_offset', 'ttl']:
            print '    %s: %d' % (key, decoded[key])
        print '    protocol: %s' % protocols[decoded['protocol']]
        print '    header checksum: %d' % decoded['checksum']
        print '    data:'
        dumphex(decoded['data'])


if __name__=='__main__':
    global begin
    global count
    global start
    start = True
    count = 0
    begin = time.time()
    if len(sys.argv) < 2:
        print 'usage: sniff.py <interface>'
        sys.exit(0)
    p = pcap.pcapObject()
    #dev = pcap.lookupdev()
    dev = sys.argv[1]
    net, mask = pcap.lookupnet(dev)
    # note:    to_ms does nothing on linux
    p.open_live(dev, 1600, 0, 100)
    #p.dump_open('dumpfile')
    #p.setfilter(string.join(sys.argv[2:],' '), 0, 0)
    client = OSCClient()
    client.connect( ("localhost", 6449) )
    # Connect to an existing database
    conn = psycopg2.connect("dbname=iplocation user=postgres password='laffi14'")
    t_send_count = threading.Thread(None, send_count_to_chuck, None, {})
    t_send_count.start()
    # Open a cursor to perform database operations
    cur = conn.cursor()
    cur.execute("SELECT begin_num, parameter FROM ip_param;")
    rows = cur.fetchall()
    this_time = time.time()
    # try-except block to catch keyboard interrupt.    Failure to shut
    # down cleanly can result in the interface not being taken out of promisc.
    # mode
    #p.setnonblock(1)
    try:
        while 1:
            p.dispatch(1, decode_ip_packet)
        # specify 'None' to dump to dumpfile, assuming you have called
        # the dump_open method
        #    p.dispatch(0, None)

        # the loop method is another way of doing things
        #    p.loop(1, print_packet)

        # as is the next() method
        # p.next() returns a (pktlen, data, timestamp) tuple
        #    apply(print_packet,p.next())
    except KeyboardInterrupt:
        print '%s' % sys.exc_type
        print 'shutting down'
        print '%d packets received, %d packets dropped, %d packets dropped by interface' % p.stats()
        start = False



# vim:set ts=4 sw=4 et:
