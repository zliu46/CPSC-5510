"""
@Purpose: This is receiver.py. This project implement rdt3.0, the final version of the stop-and-wait approach.
@using UDP as the underlying transport service. 
@Author: Zhou Liu
@Course: CPSC5510
@5/13/2024
@version 1.0
"""
from socket import *
from time import sleep
## No other imports allowed
class Receiver:
    def __init__(self):
        """Initialize the receiver with default values."""
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(('localhost', 10158)) #Port_num: 10100 + 500% SU_ID
        self.expected_seq_num = 0
        self.packet_count = 0

    def rdt_receive(self):
        """Reliably receive messages from the sender."""
        while True:
            packet, client_address = self.server_socket.recvfrom(2048)
            self.packet_count += 1
             # Simulate timeout for all the packets whose number is divisible by 6
            if self.packet_count % 6 == 0:
                print(f"Simulating timeout for packet number {self.packet_count}")
                sleep(2)  # Simulate timeout by delaying the ACK response
                continue
            # Simulate packet corruption for all the packets whose number is divisible by 3
            if self.packet_count % 3 == 0:
                print(f"Simulating corruption for packet number {self.packet_count}")
                checksum_valid = False
            else:
                checksum_valid = self.verify_checksum(packet)

            if checksum_valid and self.is_expected_sequence(packet):
                data = packet[12:].decode()
                print(f"Packet {self.packet_count} received correctly: {data}")
                self.send_ack(client_address, self.expected_seq_num)
                self.expected_seq_num = 1 - self.expected_seq_num  # Toggle expected sequence number
            else:
                print(f"Packet {self.packet_count} is corrupted or has incorrect sequence number.")
                # Resend ACK for the last correctly received packet
                self.send_ack(client_address, 1 - self.expected_seq_num)

    def create_checksum(self, packet_wo_checksum):
        """Create the checksum of the packet (MUST-HAVE DO-NOT-CHANGE)

        Args:
          packet_wo_checksum: the packet byte data (including headers except for checksum field)

        Returns:
          the checksum in bytes
        """
        s = 0
        # Add each 16-bit chunk to the sum
        for i in range(0, len(packet_wo_checksum), 2):
            w = (packet_wo_checksum[i] << 8) + (packet_wo_checksum[i+1])
            s = s + w
        # Wrap around carry bits
        s = (s >> 16) + (s & 0xffff)
        s = ~s & 0xffff
        return bytes([s >> 8, s & 0xff])

    def verify_checksum(self, packet):
        """Verify packet checksum (MUST-HAVE DO-NOT-CHANGE)

        Args:
          packet: the whole (including original checksum) packet byte data

        Returns:
          True if the packet checksum is the same as specified in the checksum field
          False otherwise
        """
        received_checksum = (packet[8] << 8) + packet[9]
        packet_wo_checksum = packet[:8] + b'\x00\x00' + packet[10:]
        calculated_checksum = (self.create_checksum(packet_wo_checksum)[0] << 8) + self.create_checksum(packet_wo_checksum)[1]
        if (received_checksum == calculated_checksum):
            return True
        else:
            return False 

    def make_ack_packet(self, ack_num, seq_num):
        """Make an ACK packet.

        Args:
          ack_num: an int tells if this packet is an ACK packet (1: ack, 0: non ack)
          seq_num: an int tells the sequence number, i.e., 0 or 1

        Returns:
          a created ACK packet in bytes
        """
        header = b'COMPNETW'
        length = len(header) + 2  # Header + checksum length
        flags = (length << 2) | (ack_num << 1) | seq_num
        flags_bytes = bytes([(flags >> 8) & 0xff, flags & 0xff])
        packet_wo_checksum = header + flags_bytes
        checksum = self.create_checksum(packet_wo_checksum)
        packet = packet_wo_checksum[:8] + checksum + packet_wo_checksum[8:]
        return packet

    def send_ack(self, client_address, seq_num):
        """Send an ACK packet.

        Args:
          client_address: the address of the sender
          seq_num: the sequence number to be acknowledged
        """
        ack_packet = self.make_ack_packet(1, seq_num)
        self.server_socket.sendto(ack_packet, client_address)
        print(f"ACK {seq_num} sent to the sender.")

    def is_packet_corrupt(self, packet):
        """Simulate corruption if packet number is divisible by 3"""
        packet_number = int.from_bytes(packet[10:12], byteorder='big')
        return packet_number % 3 == 0

    def is_expected_sequence(self, packet):
        """Check if the packet sequence number is as expected"""
        seq_num = packet[11] & 0x01  # Extracting the last bit for sequence number
        return seq_num == self.expected_seq_num

    def close(self):
        """Close the server socket."""
        self.server_socket.close()

if __name__ == "__main__":
    receiver = Receiver()
    try:
        receiver.rdt_receive()
    finally:
        receiver.close()