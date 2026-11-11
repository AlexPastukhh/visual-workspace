"""Create an editable OpenRaster (.ora) with paint layers for Krita."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED,ZIP_STORED
import sys,struct,zlib
mode=sys.argv[1] if len(sys.argv)>1 else 'v1'
root=Path(__file__).resolve().parent.parent
out=root/'output/2d'
out.mkdir(parents=True,exist_ok=True)
base=root/'assets/base.png'
if not base.exists(): raise SystemExit('Base 2D image missing: '+str(base))
w,h=600,420
def rgba_png(points):
 raw=bytearray()
 for y in range(h):
  raw.append(0)
  for x in range(w):
   paint=any((x-cx)**2+(y-cy)**2<radius**2 for cx,cy,radius in points)
   raw.extend((247,233,180,210) if paint else (0,0,0,0))
 def ch(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+ch(b'IDAT',zlib.compress(bytes(raw),6))+ch(b'IEND',b'')
coords=[(72,70,5),(177,83,6),(315,53,5)] if mode=='v1' else [(72,70,8),(177,83,8),(315,53,8),(380,155,10),(455,145,8)]
top=rgba_png(coords)
stack=f'<image w="{w}" h="{h}" name="Fortis 2D" version="0.0.3"><stack><layer name="Light marks" src="data/marks.png" x="0" y="0" opacity="1.0" visibility="visible" composite-op="svg:src-over"/><layer name="Background artwork" src="data/base.png" x="0" y="0" opacity="1.0" visibility="visible" composite-op="svg:src-over"/></stack></image>'
target=out/('scene_'+mode+'.ora')
with ZipFile(target,'w') as z:
 z.writestr('mimetype','image/openraster',compress_type=ZIP_STORED)
 z.writestr('stack.xml',stack,compress_type=ZIP_DEFLATED)
 z.writestr('data/base.png',base.read_bytes(),compress_type=ZIP_DEFLATED)
 z.writestr('data/marks.png',top,compress_type=ZIP_DEFLATED)
 z.writestr('mergedimage.png',base.read_bytes(),compress_type=ZIP_DEFLATED)
print('ORA_CREATED',target,'mode',mode)
