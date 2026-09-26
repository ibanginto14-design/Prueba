import json, urllib.request, urllib.parse, time, traceback
LOG=[]
EPS=["https://overpass-api.de/api/interpreter","https://overpass.kumi.systems/api/interpreter","https://maps.mail.ru/osm/tools/overpass/api/interpreter","https://overpass.private.coffee/api/interpreter"]
def run(bb):
    q=f"""[out:json][timeout:170];
(nwr["amenity"="place_of_worship"]["religion"="christian"]({bb});
 nwr["building"~"^(church|chapel|cathedral)$"]({bb}););
out center tags;"""
    for att in range(3):
        for url in EPS:
            try:
                data=urllib.parse.urlencode({'data':q}).encode()
                req=urllib.request.Request(url,data=data,headers={'User-Agent':'parrokiak-san-miguel-app/1.0 (github ibanginto14-design)','Accept':'application/json'})
                with urllib.request.urlopen(req,timeout=200) as r: js=json.load(r)
                LOG.append(f'ok {bb} {url} {len(js["elements"])}'); return js['elements']
            except Exception as e:
                LOG.append(f'fail {bb} {url} {e!r}'); time.sleep(8)
    return []
lats=[41.85,42.45,43.05,43.70]; lons=[-3.75,-2.70,-1.65,-0.60]
els={}
for i in range(3):
    for j in range(3):
        bb=f"{lats[i]},{lons[j]},{lats[i+1]},{lons[j+1]}"
        for el in run(bb): els[el['type'][0]+str(el['id'])]=el
out=[]
for k,el in els.items():
    t=el.get('tags',{})
    lat=el.get('lat') or el.get('center',{}).get('lat'); lon=el.get('lon') or el.get('center',{}).get('lon')
    if lat is None: continue
    out.append({'id':k,'lat':round(lat,6),'lon':round(lon,6),'n':t.get('name',''),'es':t.get('name:es',''),'eu':t.get('name:eu',''),'fr':t.get('name:fr',''),
      'b':t.get('building',''),'d':t.get('denomination',''),'pw':t.get('amenity','')=='place_of_worship'})
json.dump(out,open('sat/out/osm_churches.json','w'),ensure_ascii=False)
LOG.append(f'total {len(out)}')
open('sat/out/osm_log.txt','w').write('\n'.join(LOG))
