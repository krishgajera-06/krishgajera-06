import json,html
D=json.load(open("data/contributions.json")); days=D["days"][-371:]; P=["#161b22","#0e4429","#006d32","#26a641","#39d353"]; R=[]
for i,d in enumerate(days):
 c=i//7;r=i%7;x=42+c*14;y=42+r*14;l=max(0,min(4,int(d.get("level",0))));delay=(c+r)*.012
 R.append(f'<rect class="day" x="{x}" y="{y}" width="11" height="11" rx="2" fill="{P[l]}" style="animation-delay:{delay:.3f}s"><title>{html.escape(str(d["date"]))}: {d.get("count",0)}</title></rect>')
s=D["stats"]
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="205"><style>text{{font-family:monospace;fill:#8b949e}}.day{{opacity:0;animation:d .35s ease forwards}}@keyframes d{{to{{opacity:1}}}}</style><rect width="100%" height="100%" rx="14" fill="#0d1117" stroke="#30363d"/><text x="24" y="25" font-size="13" fill="#39d353">krish@github ~ $ github-contributions --live</text>{''.join(R)}<text x="24" y="171" font-size="12">{s["total"]:,} contributions • current streak {s["current_streak"]}d • longest {s["longest_streak"]}d</text><text x="24" y="193" font-size="10">Auto-refreshed daily by GitHub Actions</text></svg>'''
open("contrib-heatmap.svg","w").write(svg)
