import importlib.util
import pathlib
import struct
import unittest
import tempfile
from unittest.mock import patch
import zlib
P=pathlib.Path(__file__).resolve().parents[1]/'skills/blender-asset-workflow/scripts/png_privacy.py'
spec=importlib.util.spec_from_file_location('png_privacy',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
class PNGTests(unittest.TestCase):
    def test_metadata_removed_pixels_identical(self):
        # One actual RGBA pixel with PNG filter 0, decoded by stdlib zlib.
        raw=b'\0\x12\x34\x56\xff'
        header=chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,6,0,0,0))
        pixels=chunk(b'IDAT',zlib.compress(raw));end=chunk(b'IEND',b'')
        base=m.SIGNATURE+header+pixels+end
        private=b''.join(chunk(k,b'File:/private/user/scene.blend') for k in m.PRIVATE_CHUNKS)
        cleaned=m.clean_bytes(m.SIGNATURE+header+private+pixels+end)
        self.assertEqual(cleaned,base)
        self.assertEqual(zlib.decompress(cleaned[len(m.SIGNATURE)+len(header)+8:-16]),raw)
        self.assertEqual(m.clean_bytes(cleaned),cleaned)
    def test_invalid_input_rejected(self):
        for data in [b'bad',m.SIGNATURE,m.SIGNATURE+chunk(b'IEND',b'')+b'extra']:
            with self.assertRaises(ValueError):m.clean_bytes(data)

    def test_failed_write_preserves_original(self):
        data=m.SIGNATURE+chunk(b'tEXt',b'File\0/private/model.blend')+chunk(b'IEND',b'')
        with tempfile.TemporaryDirectory() as directory:
            path=pathlib.Path(directory)/'preview.png';path.write_bytes(data)
            real=m.tempfile.NamedTemporaryFile
            class FailingStream:
                def __init__(self,*args,**kwargs):self.stream=real(*args,**kwargs);self.name=self.stream.name
                def __enter__(self):return self
                def __exit__(self,*args):self.stream.close()
                def write(self,data):self.stream.write(data[:3]);raise OSError('simulated partial write')
            with patch.object(m.tempfile,'NamedTemporaryFile',FailingStream):
                with self.assertRaises(OSError):m.clean_file(path)
            self.assertEqual(path.read_bytes(),data)
            self.assertEqual(list(path.parent.iterdir()),[path])
    def test_failed_replace_preserves_original(self):
        data=m.SIGNATURE+chunk(b'tEXt',b'File\0/private/model.blend')+chunk(b'IEND',b'')
        with tempfile.TemporaryDirectory() as directory:
            path=pathlib.Path(directory)/'preview.png';path.write_bytes(data)
            with patch.object(m.os,'replace',side_effect=OSError('simulated replace failure')):
                with self.assertRaises(OSError):m.clean_file(path)
            self.assertEqual(path.read_bytes(),data)
            self.assertEqual(list(path.parent.iterdir()),[path])
