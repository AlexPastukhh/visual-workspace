#!/usr/bin/env python3
"""Draw an editable, layered 2D game character atlas without generative AI."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
import json, struct, zlib, math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "2d"
OUT.mkdir(parents=True, exist_ok=True)
SCALE = 3
SIZE = 64
HI = SIZE * SCALE
INK = (18, 39, 55, 255)
TEAL = (43, 177, 164, 255)
LIGHT = (126, 229, 209, 255)
DEEP = (24, 89, 100, 255)
ORANGE = (255, 151, 73, 255)
GOLD = (255, 213, 122, 255)
WHITE = (244, 250, 242, 255)
BLUE = (73, 164, 218, 255)
SHADOW = (9, 31, 43, 90)

def canvas():
    return bytearray(HI * HI * 4)

def pixel(buf, x, y, color):
    if 0 <= x < HI and 0 <= y < HI:
        i = (y * HI + x) * 4
        buf[i:i+4] = bytes(color)

def ellipse(buf, cx, cy, rx, ry, color):
    cx, cy, rx, ry = [int(round(v * SCALE)) for v in (cx, cy, rx, ry)]
    if rx <= 0 or ry <= 0: return
    for y in range(max(0, cy-ry), min(HI, cy+ry+1)):
        dy = (y-cy)/ry
        span = rx * math.sqrt(max(0.0, 1.0-dy*dy))
        left, right = int(cx-span), int(cx+span)
        for x in range(max(0,left), min(HI,right+1)):
            pixel(buf,x,y,color)

def polygon(buf, pts, color):
    pts=[(int(round(x*SCALE)),int(round(y*SCALE))) for x,y in pts]
    minx=max(0,min(x for x,y in pts)); maxx=min(HI-1,max(x for x,y in pts))
    miny=max(0,min(y for x,y in pts)); maxy=min(HI-1,max(y for x,y in pts))
    for y in range(miny,maxy+1):
        for x in range(minx,maxx+1):
            inside=False
            j=len(pts)-1
            for i in range(len(pts)):
                xi,yi=pts[i]; xj,yj=pts[j]
                if ((yi>y)!=(yj>y)) and x < (xj-xi)*(y-yi)/(yj-yi+1e-12)+xi:
                    inside=not inside
                j=i
            if inside: pixel(buf,x,y,color)

def line(buf, a, b, width, color):
    x1,y1=a; x2,y2=b
    steps=max(1,int(math.hypot(x2-x1,y2-y1)*SCALE*1.5))
    radius=width/2
    for i in range(steps+1):
        t=i/steps
        ellipse(buf,x1+(x2-x1)*t,y1+(y2-y1)*t,radius,radius,color)

def downsample(buf):
    out=bytearray(SIZE*SIZE*4)
    for y in range(SIZE):
        for x in range(SIZE):
            sums=[0,0,0,0]
            for sy in range(SCALE):
                for sx in range(SCALE):
                    i=(((y*SCALE+sy)*HI)+(x*SCALE+sx))*4
                    for c in range(4): sums[c]+=buf[i+c]
            j=(y*SIZE+x)*4
            out[j:j+4]=bytes((v//(SCALE*SCALE) for v in sums))
    return bytes(out)

def png_rgba(w,h,rgba):
    def chunk(tag,data):
        return struct.pack(">I",len(data))+tag+data+struct.pack(">I",zlib.crc32(tag+data)&0xffffffff)
    raw=b"".join(b"\0"+rgba[y*w*4:(y+1)*w*4] for y in range(h))
    return (b"\x89PNG\r\n\x1a\n"+
            chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,6,0,0,0))+
            chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b""))

def draw_frame(name, bob=0, stride=0, jump=0, arm=0):
    b=canvas()
    # Feet and legs, drawn behind the torso.
    hip_y=45+bob-jump
    lk=(25+stride*0.42,52-jump+abs(stride)*0.10)
    rk=(39-stride*0.42,52-jump+abs(stride)*0.10)
    lf=(22+stride,59-jump+abs(stride)*0.12)
    rf=(42-stride,59-jump+abs(stride)*0.12)
    for a,k,f in [((27,hip_y),lk,lf),((37,hip_y),rk,rf)]:
        line(b,a,k,8,INK); line(b,a,k,5,DEEP)
        ellipse(b,*k,4.1,4.1,INK); ellipse(b,*k,2.5,2.5,ORANGE)
        line(b,k,f,7,INK); line(b,k,f,4.5,TEAL)
        ellipse(b,f[0]+1,f[1],5.8,3.2,INK)
        ellipse(b,f[0]+1,f[1]-0.8,4.8,2.2,ORANGE)
    # Arms, with a clear shoulder/elbow/hand silhouette.
    for side in (-1,1):
        sx=21 if side<0 else 43
        ex=sx+side*(3+arm)
        ey=37+bob-jump
        hx=ex+side*2
        hy=43+bob-jump
        line(b,(sx,31+bob-jump),(ex,ey),8,INK)
        line(b,(sx,31+bob-jump),(ex,ey),5,TEAL)
        ellipse(b,ex,ey,4,4,INK); ellipse(b,ex,ey,2.5,2.5,GOLD)
        line(b,(ex,ey),(hx,hy),6,INK); line(b,(ex,ey),(hx,hy),3.7,LIGHT)
        ellipse(b,hx,hy,3.1,3.1,INK); ellipse(b,hx,hy,2,2,ORANGE)
    # Torso: rounded polygon with a dark outline and inset teal plate.
    y=28+bob-jump
    polygon(b,[(23,y),(41,y),(45,y+5),(43,y+18),(38,y+21),(26,y+21),(21,y+17),(19,y+5)],INK)
    polygon(b,[(24,y+1),(40,y+1),(43,y+6),(41,y+17),(37,y+19),(27,y+19),(23,y+16),(21,y+6)],TEAL)
    polygon(b,[(25,y+2),(39,y+2),(41,y+6),(39,y+9),(25,y+9),(23,y+6)],LIGHT)
    ellipse(b,32,y+13,5.5,4.5,DEEP)
    ellipse(b,32,y+13,3.2,2.5,ORANGE)
    ellipse(b,32,y+13,1.2,1.2,GOLD)
    # Head, visor and antenna.
    head_y=15+bob-jump
    line(b,(32,5+bob-jump),(32,8+bob-jump),2.5,INK)
    ellipse(b,32,4+bob-jump,2.8,2.8,ORANGE)
    ellipse(b,32,head_y,15.2,13.2,INK)
    ellipse(b,32,head_y,13.1,11.2,GOLD)
    ellipse(b,32,head_y+1,11.2,8.1,DEEP)
    ellipse(b,27.7,head_y,2.3,2.7,WHITE)
    ellipse(b,36.3,head_y,2.3,2.7,WHITE)
    ellipse(b,28.2,head_y+0.5,1.1,1.4,BLUE)
    ellipse(b,36.8,head_y+0.5,1.1,1.4,BLUE)
    line(b,(29,head_y+5),(35,head_y+5),1.2,LIGHT)
    # Small side ear pads.
    ellipse(b,18.5,head_y+1,2.4,4,ORANGE)
    ellipse(b,45.5,head_y+1,2.4,4,ORANGE)
    return downsample(b)

frames=[
    ("idle_a",dict(bob=0,stride=0,arm=0)),
    ("idle_b",dict(bob=-1,stride=0,arm=-1)),
    ("walk_a",dict(bob=0,stride=-7,arm=5)),
    ("walk_b",dict(bob=-1,stride=0,arm=-2)),
    ("walk_c",dict(bob=0,stride=7,arm=-5)),
    ("walk_d",dict(bob=1,stride=0,arm=2)),
    ("jump_a",dict(bob=0,stride=-3,jump=6,arm=-4)),
    ("jump_b",dict(bob=-1,stride=3,jump=8,arm=4)),
]
frame_rgba=[(name,draw_frame(name,**pose)) for name,pose in frames]
pngs=[(name,png_rgba(SIZE,SIZE,data)) for name,data in frame_rgba]
atlas=bytearray(8*SIZE*SIZE*4)
for i,(name,data) in enumerate(frame_rgba):
    for y in range(SIZE):
        src=y*SIZE*4; dst=(y*(8*SIZE)+i*SIZE)*4
        atlas[dst:dst+SIZE*4]=data[src:src+SIZE*4]
atlas_png=png_rgba(8*SIZE,SIZE,bytes(atlas))
(OUT/"robot_atlas.png").write_bytes(atlas_png)
for name,data in pngs:
    (OUT/f"{name}.png").write_bytes(data)
manifest={
 "canvas":[512,64],"frame_size":[64,64],
 "frames":[{"name":n,"x":i*64,"y":0,"duration_ms":120} for i,(n,_) in enumerate(frames)],
 "animations":{"idle":["idle_a","idle_b"],"walk":["walk_a","walk_b","walk_c","walk_d"],"run":["walk_a","walk_c"],"jump":["jump_a","jump_b"]},
 "source":"Hand-authored vector-like raster drawing in Python; not AI-generated."
}
(OUT/"robot_atlas.json").write_text(json.dumps(manifest,indent=2))
# Layered OpenRaster source: each frame remains separately editable in Krita.
stack=''.join(f'<layer name="{i:02d}_{name}" src="data/{name}.png" x="{i*64}" y="0" opacity="1.0" visibility="visible" composite-op="svg:src-over"/>' for i,(name,_) in enumerate(frames))
xml=f'<?xml version="1.0" encoding="UTF-8"?><image version="0.0.3" w="512" h="64" name="Game Animation MVP - Robot Sprite"><stack>{stack}</stack></image>'
with ZipFile(OUT/"robot_animation_source.ora","w") as z:
    z.writestr("mimetype","image/openraster",compress_type=ZIP_STORED)
    z.writestr("stack.xml",xml,compress_type=ZIP_DEFLATED)
    for name,data in pngs:z.writestr(f"data/{name}.png",data,compress_type=ZIP_DEFLATED)
    z.writestr("mergedimage.png",atlas_png,compress_type=ZIP_DEFLATED)
print("2D_ASSETS_CREATED",OUT)
print("ATLAS",OUT/"robot_atlas.png",len(atlas_png))
print("EDITABLE_ORA",OUT/"robot_animation_source.ora")
print("FRAMES",",".join(n for n,_ in frames))
