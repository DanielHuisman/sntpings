import netifaces
import socket
from impacket import IP6, ICMP6
from PIL import Image

net_addresses = netifaces.ifaddresses('eno1')
source_address = net_addresses[netifaces.AF_INET6][0]['addr']

raw_socket = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_ICMPV6)

payload = [ord('A') for i in range(0, 156)]
sequence_id = 0

def ping(destination_address):
    global source_address, raw_socket, payload, sequence_id

    ip = IP6.IP6()
    ip.set_ip_src(source_address)
    ip.set_ip_dst(destination_address)
    ip.set_traffic_class(0)
    ip.set_flow_label(0)
    ip.set_hop_limit(64)

    sequence_id += 1
    sequence_id = sequence_id % 65536
    icmp = ICMP6.ICMP6.Echo_Request(1, sequence_id, payload)

    ip.contains(icmp)
    ip.set_next_header(ip.child().get_ip_protocol_number())
    ip.set_payload_length(ip.child().get_size())
    icmp.calculate_checksum()

    raw_socket.sendto(icmp.get_packet(), (destination_address, 0))

image = Image.open('image_background.png')
pixels = image.load()

offset_x = int(1920 / 8)
offset_y = int(1080 / 2)

addresses = {}
for x in range(0, image.width):
    for y in range(0, image.height):
        addresses[x, y] = '2001:610:1908:a000:{0:04x}:{1:04x}:{2:02x}{3:02x}:{4:02x}{5:02x}'.format(
            offset_x + x,
            offset_y + y,
            pixels[x, y][2],
            pixels[x, y][0],
            pixels[x, y][1],
            pixels[x, y][3]
        )

print(f'Pinging {image.width}x{image.height}={image.width * image.height} pixels...')

while True:
    for x in range(0, image.width):
        for y in range(0, image.height):
            ping(addresses[x, y])
