from pathlib import Path
import json, math
p=Path(__file__).resolve().parent
p.mkdir(exist_ok=True)
rows=[
'........................',
'...........YY...........',
'..........YYYY..........',
'.........CCYYCC.........',
'........CCCCCCCC........',
'.......CCBCCCCBCC.......',
'......CCCCCCCCCCCC......',
'.....CCCCCCCCCCCCCC.....',
'.....CCCOOCCCCOOCCC.....',
'....CCCCOOCCCCOOCCCC....',
'....CCCCCCCCCCCCCCCC....',
'....CCCCCCWWCCCCCCCC....',
'....CCCCCCCWWCCCCCCC....',
'....CCCCCCCCCCCCCCCC....',
'.....CCCCCCCCCCCCCC.....',
'......PPPPPPPPPPPP......',
'.......PPP....PPP.......',
'.......PPP....PPP.......',
'......PPPP....PPPP......',
'.....RRRR......RRRR.....',
'.....RRR........RRR.....',
'....R............R......',
'........................']
pal={'Y':'#ffe18d','C':'#63e4dc','B':'#2388b2','O':'#162740','W':'#d5ffff','P':'#a683f5','R':'#ffab6b'}
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="384" height="384" viewBox="0 0 384 384"><rect width="384" height="384" fill="#141d33"/>']
for y,row in enumerate(rows):
 for x,c in enumerate(row):
  if c in pal: parts.append('<rect x="%d" y="%d" width="16" height="16" fill="%s"/>'%(x*16,y*16,pal[c]))
parts.append('</svg>')
(p/'sprite.svg').write_text(''.join(parts),encoding='utf8')
vector='''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="420" viewBox="0 0 600 420">
<defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="#102346"/><stop offset="1" stop-color="#387ca1"/></linearGradient></defs>
<rect width="600" height="420" fill="url(#sky)"/><circle cx="463" cy="92" r="48" fill="#ffd9a3"/>
<path d="M0 282 L111 132 L187 247 L283 105 L409 267 L503 156 L600 263 V420 H0Z" fill="#203e62"/>
<path d="M0 349 Q112 262 241 340 T600 320V420H0Z" fill="#186a72"/>
<g id="house"><rect x="209" y="261" width="172" height="117" rx="4" fill="#ecb877"/>
<path d="M191 270 L296 182 L399 270Z" fill="#c05b57" stroke="#803b50" stroke-width="6" stroke-linejoin="round"/>
<rect x="282" y="312" width="42" height="66" rx="6" fill="#533f5a"/>
<rect x="229" y="294" width="38" height="34" fill="#beeaf2" stroke="#755c64" stroke-width="7"/>
<rect x="340" y="294" width="24" height="34" fill="#beeaf2" stroke="#755c64" stroke-width="7"/></g>
<path d="M0 378 Q150 357 288 385 T600 372 V420H0Z" fill="#123c4a"/></svg>'''
(p/'vector.svg').write_text(vector,encoding='utf8')
faces=[]
def face(m,*v): faces.append((m,list(v)))
face('wall',(-1.25,-.8,0),(1.25,-.8,0),(1.25,-.8,1.58),(-1.25,-.8,1.58))
face('wall',(1.25,-.8,0),(1.25,.8,0),(1.25,.8,1.58),(1.25,-.8,1.58))
face('wall',(-1.25,.8,0),(-1.25,-.8,0),(-1.25,-.8,1.58),(-1.25,.8,1.58))
face('wall',(1.25,.8,0),(-1.25,.8,0),(-1.25,.8,1.58),(1.25,.8,1.58))
face('wall',(-1.25,-.8,1.58),(1.25,-.8,1.58),(0,-.8,2.23))
face('wall',(1.25,.8,1.58),(-1.25,.8,1.58),(0,.8,2.23))
face('roof',(-1.44,-1,1.55),(0,-1,2.32),(0,1,2.32),(-1.44,1,1.55))
face('roof',(0,-1,2.32),(1.44,-1,1.55),(1.44,1,1.55),(0,1,2.32))
face('door',(-.25,-.815,0),(.25,-.815,0),(.25,-.815,1.10),(-.25,-.815,1.10))
for a,b in ((-.97,-.6),(.6,.97)): face('glass',(a,-.82,.85),(b,-.82,.85),(b,-.82,1.24),(a,-.82,1.24))
colors={'wall':'#eeb57d','roof':'#bc5f5e','door':'#68445e','glass':'#94dcf2'}
obj=['# Procedural 3D house, native OBJ vertices and polygon faces','mtllib house.mtl','o ProceduralHouse']
count=1
for m,vs in faces:
 obj.append('usemtl '+m)
 obj+=['v '+' '.join(map(str,v)) for v in vs]
 obj.append('f '+' '.join(map(str,range(count,count+len(vs)))))
 count+=len(vs)
(p/'house.obj').write_text('\n'.join(obj)+'\n',encoding='utf8')
mtl=[]
for m,c in colors.items():
 rgb=[int(c[i:i+2],16)/255 for i in (1,3,5)]
 mtl.append('newmtl %s\nKd %s\nKa 0.1 0.1 0.1'%(m,' '.join('%.4f'%v for v in rgb)))
(p/'house.mtl').write_text('\n\n'.join(mtl)+'\n',encoding='utf8')
# The preview projects the actual faces of the generated 3D mesh, not an imagined picture.
eye=(4.2,-5.8,3.35); at=(0,0,1)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(v):return tuple(x/math.sqrt(dot(v,v)) for x in v)
fw=norm(sub(at,eye)); right=norm(cross(fw,(0,0,1)));up=norm(cross(right,fw))
def project(v):
 d=sub(v,at)
 return 370+140*dot(d,right),250-140*dot(d,up)
def shaded(c,k):return '#'+''.join('%02x'%max(0,min(255,round(int(c[i:i+2],16)*k))) for i in (1,3,5))
polys=[]
for idx in [1,0,7,4,8,9,10]:
 m,vs=faces[idx]
 n=norm(cross(sub(vs[1],vs[0]),sub(vs[2],vs[0])))
 light=norm((-.35,-.75,1))
 lum=.76+.24*abs(dot(n,light))
 depth=sum(dot(sub(v,eye),fw) for v in vs)/len(vs)
 pts=' '.join('%.1f,%.1f'%project(v) for v in vs)
 polys.append((depth,'<polygon points="%s" fill="%s" stroke="#29334a" stroke-width="2" stroke-linejoin="round"/>'%(pts,shaded(colors[m],lum))))
## Painter-order corrected: visible walls, roof, gable, then facade decorations.
preview='<svg xmlns="http://www.w3.org/2000/svg" width="740" height="500"><rect width="740" height="500" fill="#e0edf2"/><ellipse cx="370" cy="424" rx="232" ry="42" fill="#bdcfc7"/>'
preview+=''.join(s for _,s in polys)+'</svg>'
(p/'house_preview.svg').write_text(preview,encoding='utf8')
(p/'report.json').write_text(json.dumps({'2d':'SVG paths and individual pixels; raster output via resvg','3d':'OBJ polygon geometry; SVG orthographic preview generated from same faces','mesh_faces':len(faces),'mesh_vertices':sum(len(vs) for _,vs in faces),'warning':'Blender and Godot not involved yet'},ensure_ascii=False,indent=2),encoding='utf8')
print('READY','files=',len(list(p.glob('*.svg'))),len(list(p.glob('*.obj'))))
