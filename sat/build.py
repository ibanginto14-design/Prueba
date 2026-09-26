import json, math, os, io, time, concurrent.futures as cf, urllib.request
from PIL import Image
P=json.load(open('sat/params.json'))
OUT='sat/out'; os.makedirs(OUT,exist_ok=True)
UA={'User-Agent':'parrokiak-san-miguel-app/1.0 (non-commercial parish map; contact via github ibanginto14-design)'}
def tx(lon,z): return (lon+180)/360*2**z
def ty(lat,z):
    r=math.radians(lat); return (1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*2**z
cache={}
def get(z,x,y):
    k=(z,x,y)
    if k in cache: return cache[k]
    url=P['layer'].format(z=z,x=x,y=y)
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30) as r:
                im=Image.open(io.BytesIO(r.read())).convert('RGB'); cache[k]=im; return im
        except Exception as e:
            time.sleep(1+a*2)
    print('FAIL',url); im=Image.new('RGB',(256,256),(20,40,50)); cache[k]=im; return im
def fetch_all(keys):
    with cf.ThreadPoolExecutor(6) as ex: list(ex.map(lambda k:get(*k),keys))
meta={'attribution':'Sentinel-2 cloudless – https://s2maps.eu by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2016 & 2017)','mosaics':[],'patches':[]}
for R in P['regions']:
    z=R['z']; w,s,e,n=R['bbox']
    x0,x1=int(tx(w,z)),int(tx(e,z)); y0,y1=int(ty(n,z)),int(ty(s,z))
    keys=[(z,x,y) for x in range(x0,x1+1) for y in range(y0,y1+1)]
    print(R['name'],len(keys)); fetch_all(keys)
    cx,cy=R['chunks']; nx=x1-x0+1; ny=y1-y0+1
    xs=[x0+round(i*nx/cx) for i in range(cx+1)]; ys=[y0+round(j*ny/cy) for j in range(cy+1)]
    for i in range(cx):
        for j in range(cy):
            ax,bx,ay,by=xs[i],xs[i+1],ys[j],ys[j+1]
            im=Image.new('RGB',((bx-ax)*256,(by-ay)*256))
            for x in range(ax,bx):
                for y in range(ay,by): im.paste(get(z,x,y),((x-ax)*256,(y-ay)*256))
            fn=f"{R['name']}_{i}_{j}.jpg"; im.save(f'{OUT}/{fn}',quality=72,optimize=True,progressive=True)
            meta['mosaics'].append({'f':fn,'z':z,'x0':ax,'y0':ay,'x1':bx,'y1':by})
    cache.clear()
pz=P['patches']['z']; r=P['patches']['r']
keys=set()
for p in P['patches']['points']:
    cxp,cyp=int(tx(p['lon'],pz)),int(ty(p['lat'],pz))
    for dx in range(-r,r+1):
        for dy in range(-r,r+1): keys.add((pz,cxp+dx,cyp+dy))
print('patches',len(keys)); fetch_all(sorted(keys))
for p in P['patches']['points']:
    cxp,cyp=int(tx(p['lon'],pz)),int(ty(p['lat'],pz)); n=2*r+1
    im=Image.new('RGB',(n*256,n*256))
    for dx in range(-r,r+1):
        for dy in range(-r,r+1): im.paste(get(pz,cxp+dx,cyp+dy),((dx+r)*256,(dy+r)*256))
    fn=f"sm_{p['i']}.jpg"; im.save(f'{OUT}/{fn}',quality=74,optimize=True,progressive=True)
    meta['patches'].append({'i':p['i'],'f':fn,'z':pz,'x0':cxp-r,'y0':cyp-r,'n':n})
json.dump(meta,open(f'{OUT}/meta.json','w'))
tot=sum(os.path.getsize(f'{OUT}/{f}') for f in os.listdir(OUT)); print('bytes',tot)
