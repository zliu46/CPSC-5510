"""
@Purpose: This is sender.py. This project implement rdt3.0, the final version of the stop-and-wait approach.
@using UDP as the underlying transport service. 
@Author: Zhou Liu
@Course: CPSC5510
@5/13/2024
@version 1.0
"""
from socket import *

class Sender:
    def __init__(self):
        """ 
        Initialize the sender with default values.
        """
        self.receiver_host = 'localhost'
        self.receiver_port = 10158  #Port_num: 10100 + 500% SU_ID
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.settimeout(1.0)  # Timeout for socket operations in seconds
        self.seq_num = 0  # Sequence number (0 or 1)
        self.packet_num = 1  # Packet number for logging

    def rdt_send(self, app_msg_str):
        """Reliably send a message to the receiver.

        Args:
          app_msg_str: the message string (to be put in the data field of the packet)
        """
        print(f"original message string: {app_msg_str}")
        packet = self.make_packet(app_msg_str, 0, self.seq_num)
        print(f"packet created: {packet}")

        ack_received = False
        
        while not ack_received:
            try:
                self.sock.sendto(packet, (self.receiver_host, self.receiver_port))
                print(f"packet num.{self.packet_num} is successfully sent to the receiver.")
                
                response, _ = self.sock.recvfrom(1024)
                
                if self.verify_checksum(response) and self.is_ack(response, self.seq_num):
                    ack_received = True
                    print(f"packet is received correctly: seq. num = ACK num {self.seq_num}. all done!")
                else:
                    print(f"receiver acked the previous pkt, resend!\n[ACK-Previous retransmission]: {app_msg_str}")
            
            except timeout:
                print(f"socket timeout! Resend!\n[timeout retransmission]: {app_msg_str}")
            
            self.packet_num += 1
        
        self.seq_num = 1 - self.seq_num  # Toggle sequence number

    def create_checksum(self, packet_wo_checksum):
        """create the checksum of the packet (MUST-HAVE DO-NOT-CHANGE)

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
        """verify packet checksum (MUST-HAVE DO-NOT-CHANGE)

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

    def make_packet(self, data_str, ack, seq_num):
        """Make a packet (MUST-HAVE DO-NOT-CHANGE)

        Args:
          data_str: the string of the data (to be put in the Data area)
          ack: an int tells if this packet is an ACK packet (1: ack, 0: non ack)
          seq_num: an int tells the sequence number, i.e., 0 or 1

        Returns:
          a created packet in bytes
        """
        header = b'COMPNETW'
        data = data_str.encode()
        # Header + checksum + data length
        length = len(header) + 2 + len(data) 
        flags = (length << 2) | (ack << 1) | seq_num
        flags_bytes = bytes([(flags >> 8) & 0xff, flags & 0xff])
        packet_wo_checksum = header + flags_bytes + data
        checksum = self.create_checksum(packet_wo_checksum)
        packet = packet_wo_checksum[:8] + checksum + packet_wo_checksum[8:]
        return packet

    def is_ack(self, packet, expected_seq_num):
        """Check if the packet is an acknowledgment for the expected sequence number."""
        length_flags = (packet[10] << 8) + packet[11]
        ack = (length_flags >> 1) & 1
        seq = length_flags & 1
        return ack == 1 and seq == expected_seq_num

if __name__ == "__main__":
    sender = Sender()
    sender.rdt_send("msg1")
    sender.rdt_send("msg2")
    sender.rdt_send("msg3")
    sender.rdt_send("msg4")
    sender.rdt_send("msg5")
    sender.rdt_send("msg6")
    sender.rdt_send("msg7")
