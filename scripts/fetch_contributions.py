import json,requests
from bs4 import BeautifulSoup
U="krishgajera-06"
r=requests.get(f"https://github.com/users/{U}/contributions",headers={"User-Agent":"Mozilla/5.0"},timeout=30);r.raise_for_status()
s=BeautifulSoup(r.text,"html.parser"); days=[]
for e in s.select("[data-date][data-level]"):
 d=e.get("data-date"); level=int(e.get("data-level","0")); label=e.get("aria-label",""); count=0
 try: count=int(label.split(" contribution")[0].replace(",",""))
 except: pass
 days.append({"date":d,"count":count,"level":level})
days=sorted({x["date"]:x for x in days}.values(),key=lambda x:x["date"])
total=sum(x["count"] for x in days); longest=cur=0
for x in days:
 cur=cur+1 if x["count"]>0 else 0; longest=max(longest,cur)
streak=0
for x in reversed(days):
 if x["count"]>0: streak+=1
 else: break
json.dump({"username":U,"days":days,"stats":{"total":total,"current_streak":streak,"longest_streak":longest}},open("data/contributions.json","w"),indent=2)
