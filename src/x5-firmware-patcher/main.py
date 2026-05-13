import zlib
import sys
import os
import struct
from dataclasses import dataclass
from typing import ClassVar

"""
HEADER FORMAT:
    MAGIC: 4
    HEADER_CHECKSUM: 4
    VERSION_TIME_1: 4
    TOTAL_SIZE: 4
    PACKET_ID: 8
    FIRMWARE_CHECKSUM: 4
    VERSION_TIME_2: 4
    RESERVED: 32
"""
HEADER_FORMAT = '<4sIII8s4sI32s'  # 4+4+4+4+8+4+4+32 = 64 bytes

MAGICS = {
    "0x27051956": "FIRMWARE_UPDATE",
    "0x23424f4f": "FIRMWARE_DUMP",
}

def debug(msg):
    caller_name = sys._getframe(1).f_code.co_name
    print(f"DEBUG({caller_name}): {msg}")

@dataclass
class FirmwareHeader:
    magic: bytes
    header_checksum: bytes
    version_time_1: int
    total_size: int
    packet_id: int
    firmware_checksum: bytes
    version_time_2: int
    reserved: bytes
    
    # Total size of the header in bytes
    SIZE: ClassVar[int] = struct.calcsize(HEADER_FORMAT)
    
    @classmethod
    def from_bytes(cls, data: bytes):
        """Parse header from 64 bytes of binary data."""
        if len(data) != cls.SIZE:
            raise ValueError(f"Expected {cls.SIZE} bytes, got {len(data)}")
        unpacked = struct.unpack(HEADER_FORMAT, data)
        return cls(*unpacked)
    
    def to_bytes(self) -> bytes:
        """Convert header back to 64 bytes of binary data."""
        return struct.pack(HEADER_FORMAT, 
                          self.magic, self.header_checksum, self.version_time_1, self.total_size,
                          self.packet_id, self.firmware_checksum, self.version_time_2, self.reserved)
    
    def reset_header_checksum(self):
        """Set the header_checksum to zero."""
        self.header_checksum = b'\x00\x00\x00\x00'


def to_hex(value):
    match value:
        case int():
            return f"{value:#x}"  # Uses # to include 0x prefix
        case bytes():
            return '0x' + value.hex()  # Add 0x to the hex string
        case _:
            # For any other type, try to convert to int first
            try:
                return f"{int(value):#x}"
            except (ValueError, TypeError):
                raise TypeError(f"Cannot convert {value} to hex")

def read_bytes_range(file_path, skip, count):
    with open(file_path, 'rb') as f:
        f.seek(skip)           # Skip to the start position
        data = f.read(count)   # Read 'count' bytes
    return data

def calculate_crc32(file_path, skip=0):
    # Read file in chunks and update hash
    chunk_size = 8192  # 8KB chunks
    with open(file_path, 'rb') as f:
        f.seek(skip)  # Skip the first "skip" bytes
        crc = 0
        while chunk := f.read(chunk_size):
            crc = zlib.crc32(chunk, crc)
    return crc & 0xFFFFFFFF  # Ensure unsigned 32-bit value


def check_header(file_path):
    magic = "0x" + read_bytes_range(file_path, skip=0, count=4).hex()
    debug(magic)
    try:
        return MAGICS[magic]
    except KeyError as e:
        return "UNKNOWN"

def check_valid_header(file_path):
    header = FirmwareHeader.from_bytes(read_bytes_range(file_path, skip=0, count=64))
    debug("HEADER MAGIC: " + to_hex(header.magic))
    debug("HEADER FW CHECKSUM: " + to_hex(header.firmware_checksum))

    firmware_checksum = calculate_crc32(file_path, skip=64)
    debug(f"CALCULATED FW CHECKSUM: {to_hex(firmware_checksum)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <firmware_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Check if file exists
    if not os.path.isfile(file_path):
        print(f"Error! File not found: {file_path}")
        exit(1)

    # 1. Check if it is a firmware update file or a dump (header is there?)
    #   1a. If firmware update, check if header is valid
    # 2. Correct/generate header and write new firmware file

    file_type = check_header(file_path)

    match file_type:
        case "FIRMWARE_UPDATE":
            print("FILE TYPE: Firmware update file with header detected")
            check_valid_header(file_path)
        case "FIRMWARE_DUMP":
            print("FILE TYPE: Firmware dump without header detected")
        case _:
            print("FILE TYPE: Error, invalid firmware file")
    
