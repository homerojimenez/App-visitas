import requests, re, sys, json, io, concurrent.futures as cf
import pyarrow.parquet as pq, pyarrow as pa
from shapely import wkb
from shapely.geometry import mapping, box
BASE="https://overturemaps-us-west-2.s3.amazonaws.com/"
REL="release/2026-09-23.1/"
import os
BB=tuple(map(float,os.environ.get("BB","-4.1480,40.9330,-4.0990,40.9620").split(",")))
S=requests.Session()
class RF(io.RawIOBase):
    def __init__(s,url):
        s.url=url; s.pos=0
        for a in range(8):
            try:
                r=requests.head(url,timeout=30); s.size=int(r.headers['Content-Length']); break
            except Exception as e:
                import time; time.sleep(1+a)
    def seekable(s): return True
    def readable(s): return True
    def tell(s): return s.pos
    def seek(s,o,w=0):
        s.pos = o if w==0 else (s.pos+o if w==1 else s.size+o); return s.pos
    def read(s,n=-1):
        if n is None or n<0: n=s.size-s.pos
        if n==0 or s.pos>=s.size: return b''
        end=min(s.size,s.pos+n)-1
        for a in range(8):
            try:
                r=requests.get(s.url,headers={'Range':f'bytes={s.pos}-{end}'},timeout=60); d=r.content; break
            except Exception as e:
                import time; time.sleep(1+a)
        s.pos+=len(d); return d
    def readinto(s,b):
        d=s.read(len(b)); b[:len(d)]=d; return len(d)
def keys(prefix):
    out=[];tok=None
    while True:
        u=BASE+f"?list-type=2&prefix={prefix}"+(f"&continuation-token={requests.utils.quote(tok)}" if tok else "")
        d=S.get(u,timeout=30).text
        out+=re.findall(r'<Key>(.*?)</Key>',d)
        m=re.search(r'<NextContinuationToken>(.*?)</NextContinuationToken>',d)
        if not m: break
        tok=m.group(1)
    return [k for k in out if k.endswith('.parquet')]
def rg_hits(md):
    sch=md.schema.to_arrow_schema()
    names=[md.schema.column(i).path for i in range(md.num_columns)]
    idx={n:i for i,n in enumerate(names)}
    hits=[]
    for g in range(md.num_row_groups):
        rg=md.row_group(g)
        try:
            xmin=rg.column(idx['bbox.xmin']).statistics.min; xmax=rg.column(idx['bbox.xmax']).statistics.max
            ymin=rg.column(idx['bbox.ymin']).statistics.min; ymax=rg.column(idx['bbox.ymax']).statistics.max
        except Exception as e:
            continue
        if xmax<BB[0] or xmin>BB[2] or ymax<BB[1] or ymin>BB[3]: continue
        hits.append(g)
    return hits
def process(key, cols):
    f=RF(BASE+key); pf=pq.ParquetFile(f)
    hits=rg_hits(pf.metadata)
    feats=[]
    for g in hits:
        t=pf.read_row_group(g,columns=cols+['bbox','geometry']).to_pylist()
        for r in t:
            b=r['bbox']
            if b['xmax']<BB[0] or b['xmin']>BB[2] or b['ymax']<BB[1] or b['ymin']>BB[3]: continue
            geom=wkb.loads(r['geometry'])
            props={k:r[k] for k in cols}
            feats.append((geom,props))
    return key,feats
def run(theme,typ,cols,out,simplify=0.0):
    ks=keys(f"{REL}theme={theme}/type={typ}/")
    print(theme,typ,len(ks),'files',flush=True)
    allf=[]
    with cf.ThreadPoolExecutor(6) as ex:
        for key,feats in ex.map(lambda k: process(k,cols), ks):
            if feats: print(' hit',key[-60:],len(feats),flush=True)
            allf+=feats
    clip=box(*BB)
    fc={'type':'FeatureCollection','features':[]}
    for g,p in allf:
        g=g.intersection(clip) if not clip.contains(g) else g
        if g.is_empty: continue
        if simplify: g=g.simplify(simplify,preserve_topology=True)
        fc['features'].append({'type':'Feature','geometry':mapping(g),'properties':p})
    json.dump(fc,open(out,'w'),separators=(',',':'))
    print('wrote',out,len(fc['features']),flush=True)
which=sys.argv[1]
if which=='seg': run('transportation','segment',['class','subtype','names'],os.environ.get('OUT','seg_raw.json'))
if which=='bld': run('buildings','building',['height'],'bld_raw.json',0.000005)
if which=='water': run('base','water',['class','subtype','names'],os.environ.get('OUT','water_raw.json'))
if which=='lu': run('base','land_use',['class','subtype','names'],os.environ.get('OUT','lu_raw.json'))
if which=='lc': run('base','land_cover',['subtype'],'lc_raw.json',0.00002)
