#!/usr/bin/env python3
"""Refresh a static OSM chain-store snapshot. Keep previous data if any request fails."""
import json, os, pathlib, time, urllib.parse, urllib.request, datetime
PATTERNS = {"uniqlo":"UNIQLO|ユニクロ","gu":"^GU$|ジーユー","daiso":"DAISO|ダイソー|ザ・ダイソー","muji":"MUJI|無印良品","nitori":"NITORI|ニトリ","gyomu":"業務スーパー","donki":"ドン・キホーテ|ドンキホーテ|Donki","starbucks":"Starbucks|スターバックス"}
import re
# Mainland Tokyo / Kanagawa coverage; approximate rectangles, not prefecture boundaries.
BOXES=[(35.48,138.90,35.80,139.40),(35.48,139.40,35.85,139.95),(35.12,138.90,35.48,139.40),(35.12,139.40,35.68,139.85)]
HOSTS=["https://overpass.kumi.systems/api/interpreter","https://overpass.private.coffee/api/interpreter","https://overpass-api.de/api/interpreter"]
regex="|".join("(?:"+p+")" for p in PATTERNS.values())
all_stores={}
for i,(s,w,n,e) in enumerate(BOXES):
    bbox=f"({s},{w},{n},{e})"
    q=f'[out:json][timeout:120];(nwr["brand"~"{regex}",i]{bbox};nwr["name"~"{regex}",i]{bbox};);out center tags;'
    payload=urllib.parse.urlencode({"data":q}).encode()
    data=None
    for host in HOSTS:
        try:
            req=urllib.request.Request(host,data=payload,headers={"User-Agent":"StoreNearbyMap/1.0 (https://github.com/hirabomasaya829-ai/store-nearby-map; public OSM snapshot)","Accept":"application/json","Content-Type":"application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req,timeout=150) as response: data=json.load(response)
            if not isinstance(data.get("elements"),list): raise ValueError("No elements")
            break
        except Exception as exc:
            print(f"Box {i+1}: {host} failed: {exc}",flush=True)
            time.sleep(3)
    if data is None: raise RuntimeError(f"Box {i+1} failed; existing snapshot preserved")
    for el in data["elements"]:
        tags=el.get("tags",{})
        name=tags.get("name","")
        brand_tag=tags.get("brand","")
        brand=next((k for k,p in PATTERNS.items() if re.search(p,name,re.I) or re.search(p,brand_tag,re.I)),None)
        if not brand: continue
        center=el.get("center",el)
        lat,lon=center.get("lat"),center.get("lon")
        if not isinstance(lat,(int,float)) or not isinstance(lon,(int,float)): continue
        key=f'{el["type"]}/{el["id"]}'
        all_stores[key]={"brand":brand,"name":(name or brand_tag or "店舗")[:100],"lat":lat,"lon":lon}
    print(f"Box {i+1} complete: {len(data['elements'])} elements",flush=True)
    time.sleep(5)
out={"updatedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"coverage":"東京都・神奈川県の本土周辺（矩形による概算）","stores":list(all_stores.values())}
path=pathlib.Path("public/data/stores.json")
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(out,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
print(f"Saved {len(all_stores)} stores")
