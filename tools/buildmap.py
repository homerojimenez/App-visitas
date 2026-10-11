import json, math, sys, networkx as nx
D='/tmp/claude-0/-home-user-App-visitas/337edbc6-130b-5668-97df-f033ed5dc189/scratchpad/map/'
def R(c): 
    if isinstance(c[0],(int,float)): return [round(c[0],5),round(c[1],5)]
    return [R(x) for x in c]
def feat(f,props):
    g=f['geometry']; g={'type':g['type'],'coordinates':R(g['coordinates'])}
    return {'type':'Feature','geometry':g,'properties':props}
out={}
seg=json.load(open(D+'seg_raw.json'))
roads=[]
for f in seg['features']:
    p=f['properties']; 
    if p.get('subtype')=='water': continue
    n=(p.get('names') or {}).get('primary') if p.get('names') else None
    roads.append(feat(f,{'c':p.get('class') or p.get('subtype'),'s':p.get('subtype'),**({'n':n} if n else {})}))
out['roads']={'type':'FeatureCollection','features':roads}
b=json.load(open(D+'bld_raw.json'))
out['buildings']={'type':'FeatureCollection','features':[feat(f,{}) for f in b['features'] if f['geometry']['type'] in ('Polygon','MultiPolygon')]}
w=json.load(open(D+'water_raw.json'))
out['water']={'type':'FeatureCollection','features':[feat(f,{'c':f['properties'].get('subtype') or f['properties'].get('class')}) for f in w['features']]}
lu=json.load(open(D+'lu_raw.json'))
out['landuse']={'type':'FeatureCollection','features':[feat(f,{'c':f['properties'].get('class'),'s':f['properties'].get('subtype')}) for f in lu['features'] if f['geometry']['type'] in ('Polygon','MultiPolygon')]}
lc=json.load(open(D+'lc_raw.json'))
out['landcover']={'type':'FeatureCollection','features':[feat(f,{'s':f['properties'].get('subtype')}) for f in lc['features'] if f['geometry']['type'] in ('Polygon','MultiPolygon')]}
from collections import Counter
print('road classes',Counter(f['properties']['c'] for f in roads).most_common(20))
print('lu',Counter(f['properties']['c'] for f in out['landuse']['features']).most_common(15))
print('lc',Counter(f['properties']['s'] for f in out['landcover']['features']).most_common(10))
print('water',Counter(f['properties']['c'] for f in out['water']['features']).most_common(10))
json.dump(out,open(D+'map.json','w'),separators=(',',':'))
# graph
def hav(a,b):
    R0=6371000; la1,lo1,la2,lo2=map(math.radians,[a[1],a[0],b[1],b[0]])
    return 2*R0*math.asin(math.sqrt(math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2))
G=nx.Graph()
bad={'motorway','trunk','rail','subway','tram','unknown_rail'}
for f in seg['features']:
    p=f['properties']
    if p.get('subtype')!='road' or p.get('class') in ('motorway','trunk'): continue
    gs=f['geometry']; lines=[gs['coordinates']] if gs['type']=='LineString' else gs['coordinates']
    for L in lines:
        pts=[(round(c[0],6),round(c[1],6)) for c in L]
        for a,c in zip(pts,pts[1:]):
            d=hav(a,c)
            # prefer pedestrian streets slightly
            k=0.85 if p.get('class') in ('pedestrian','footway','steps','living_street','path') else 1.0
            G.add_edge(a,c,w=d*k,d=d)
print('graph',G.number_of_nodes(),G.number_of_edges())
nodes=list(G.nodes)
import pickle; pickle.dump(G,open(D+'graph.pkl','wb'))
