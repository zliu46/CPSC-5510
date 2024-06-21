"""
@Purpose: This is util.py. This project implement rdt3.0, the final version of the stop-and-wait approach.
@using UDP as the underlying transport service. 
@Author: Zhou Liu
@Course: CPSC5510
@5/13/2024
@version 1.0
"""
def create_checksum(packet_wo_checksum):
    """create the checksum of the packet (MUST-HAVE DO-NOT-CHANGE)

    Args:
      packet_wo_checksum: the packet byte data (including headers except for checksum field)

    Returns:
      the checksum in bytes

    """
    s = 0
    # Add each 16-bit chunk to the sum
    for i in range(0, len(packet_wo_checksum), 2):
        if i+1 < len(packet_wo_checksum):
            w = (packet_wo_checksum[i] << 8) + packet_wo_checksum[i+1]
        else:
            w = (packet_wo_checksum[i] << 8)
        s = s + w
    # Wrap around carry bits
    s = (s >> 16) + (s & 0xffff)
    s = ~s & 0xffff
    return bytes([s >> 8, s & 0xff])


def verify_checksum(packet):
    """verify packet checksum (MUST-HAVE DO-NOT-CHANGE)

    Args:
      packet: the whole (including original checksum) packet byte data

    Returns:
      True if the packet checksum is the same as specified in the checksum field
      False otherwise

    """
    received_checksum = (packet[8] << 8) + packet[9]
    packet_wo_checksum = packet[:8] + b'\x00\x00' + packet[10:]
    calculated_checksum = (create_checksum(packet_wo_checksum)[0] << 8) + create_checksum(packet_wo_checksum)[1]
    if (received_checksum == calculated_checksum):
            return True
    else:
            return False 
def make_packet(data_str, ack_num, seq_num):
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
    length = len(header) + 2 + len(data)  # Header + checksum + data length
    flags = (length << 2) | (ack_num << 1) | seq_num
    flags_bytes = flags.to_bytes(2, byteorder='big')
    packet_wo_checksum = header + b'\x00\x00' + flags_bytes + data
    checksum = create_checksum(packet_wo_checksum)
    packet = header + checksum + flags_bytes + data
    return packet
    # make sure your packet follows the required format!

###### These three functions will be automatically tested while grading. ######
###### Hence, your implementation should NOT make any changes to         ######
###### the above function names and args list.                           ######
###### You can have other helper functions if needed.                    ######  
