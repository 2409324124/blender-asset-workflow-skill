"""Remove known private chunks; not a complete PNG image validator/decoder."""
from pathlib import Path
import os
import tempfile
import struct
import zlib

SIGNATURE = b'\x89PNG\r\n\x1a\n'
PRIVATE_CHUNKS = {b'tEXt', b'zTXt', b'iTXt', b'eXIf', b'tIME'}

def clean_bytes(data):
    if not data.startswith(SIGNATURE):
        raise ValueError('not a PNG')
    result = bytearray(SIGNATURE)
    offset = 8
    ended = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError('truncated PNG chunk')
        size = struct.unpack('>I', data[offset:offset+4])[0]
        end = offset + size + 12
        if end > len(data):
            raise ValueError('truncated PNG payload')
        kind = data[offset+4:offset+8]
        payload = data[offset+8:end-4]
        crc = struct.unpack('>I', data[end-4:end])[0]
        if zlib.crc32(kind + payload) & 0xffffffff != crc:
            raise ValueError('invalid PNG CRC')
        if kind not in PRIVATE_CHUNKS:
            result.extend(data[offset:end])
        offset = end
        if kind == b'IEND':
            if size or offset != len(data):
                raise ValueError('invalid PNG end/trailing data')
            ended = True
            break
    if not ended:
        raise ValueError('missing PNG end')
    return bytes(result)

def clean_file(path):
    """Only call on a newly generated preview owned by this invocation."""
    path = Path(path)
    original = path.read_bytes()
    cleaned = clean_bytes(original)
    if cleaned != original:
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='wb', dir=path.parent,
                                             prefix='.' + path.name + '.',
                                             suffix='.tmp', delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(cleaned)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
