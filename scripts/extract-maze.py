# Generates src/lib/maze.json from the vector PDF: python scripts/extract-maze.py src/lib/maze.json
import re,json,sys
d=open('assets/CHE-doolhof-2026-A4.pdf','rb').read()
c=d[d.index(b'stream')+7:d.index(b'endstream')].decode('latin1')
X0,Y0,S=55.105511811023618,661.2663779527558745,10.6015748031496084
COLS,ROWS=44,53
col=lambda x:(x-X0)/S; row=lambda y:(Y0-y)/S
cells={}; fill=None; w=None; pts=[]; h={}; v={}; labels=[]
toks=c.split('\n')
for t in toks:
  p=t.split()
  if t.endswith(' rg') : fill=' '.join(p[:3])
  elif t.endswith(' g'): fill=p[0]
  elif t.endswith(' re') and abs(float(p[2])-S)<.01:
    cells[(round(row(float(p[1]))),round(col(float(p[0]))))]=fill
  elif t.endswith(' w'): w=float(p[0])
  elif t.endswith(' m'): pts=[(float(p[0]),float(p[1]))]
  elif t.endswith(' l'): pts.append((float(p[0]),float(p[1])))
  elif t=='S' and len(pts)==2 and w in (0.6236220472440945,1.8425196850393704):
    (x1,y1),(x2,y2)=pts; k=1 if w<1 else 2
    if abs(y1-y2)<.01:
      r=round(row(y1))
      a,b=sorted([round(col(x1)),round(col(x2))])
      for cc in range(a,b): h[(r,cc)]=max(h.get((r,cc),0),k)
    elif abs(x1-x2)<.01:
      cc=round(col(x1))
      a,b=sorted([round(row(y1)),round(row(y2))])
      for r in range(a,b): v[(r,cc)]=max(v.get((r,cc),0),k)
    else: print('diag',pts,file=sys.stderr)
for m in re.finditer(r'/F2 ([\d.]+) Tf\n[^\n]*\n[\d.]+ ([\d.]+) [\d.]+ rg\n0 Tr\n([\d.]+) ([\d.]+) Td\n\((.*?)\) Tj',c):
  size,g,x,y,txt=float(m[1]),float(m[2]),float(m[3]),float(m[4]),m[5]
  if -2<row(y)<56 and txt!='CHE': labels.append([round(col(x),2),round(row(y),2),round(size/S,3),txt,int(g>0.5)])
fills=sorted(set(cells.values())); print(fills,file=sys.stderr)
out={'cols':COLS,'rows':ROWS,
 'fills':fills,
 'cells':[''.join(str(fills.index(cells[(r,cc)])) if (r,cc) in cells else '.' for cc in range(COLS)) for r in range(ROWS)],
 'h':[''.join(str(h.get((r,cc),0)) for cc in range(COLS)) for r in range(ROWS+1)],
 'v':[''.join(str(v.get((r,cc),0)) for cc in range(COLS+1)) for r in range(ROWS)],
 'labels':labels}
json.dump(out,open(sys.argv[1],'w'))
# boundary openings
for (r,cc) in cells:
  for dr,dc,wall in ((-1,0,h.get((r,cc),0)),(1,0,h.get((r+1,cc),0)),(0,-1,v.get((r,cc),0)),(0,1,v.get((r,cc+1),0))):
    if not wall and (r+dr,cc+dc) not in cells: print('open to outside',r,cc,dr,dc,file=sys.stderr)
print('exit line', row(181.47), col(139.4646), 'start', row(628.05), col(257.04),file=sys.stderr)
