import pdfplumber, json, glob, re, sys
POS=r'^\(+\s*(명|동|형|부|전|접|대|감|분사)(?:\1)?\s*\)+$'
def undouble(t):
    if len(t)>=4 and len(t)%2==0 and all(t[i]==t[i+1] for i in range(0,len(t),2)): return t[::2]
    return t
rows={}
for f in sorted(glob.glob(sys.argv[1]+"/*.pdf")):
    for p in pdfplumber.open(f).pages:
        ws=p.dedupe_chars().extract_words()
        anchors=[(w['top'],int(w['text'])) for w in ws if w['x0']<90 and w['top']>40 and w['text'].isdigit()]
        hs=sorted(set(e['top'] for e in p.edges if e['orientation']=='h'))
        bounds={}
        for t,n in anchors:
            bounds[n]=(max([h for h in hs if h<=t] or [0]), min([h for h in hs if h>=t+8] or [9999]))
        cells={}
        for w in ws:
            if w['top']<40 or w['x0']<90 or (300<w['x0']<322 and w['text'].isdigit()): continue
            c=(w['top']+w['bottom'])/2
            top,n=min(anchors,key=lambda a:abs(a[0]+5-c))
            if abs(top+5-c)>16: continue
            b=bounds[n]
            if w['top']<b[0]-0.5 or w['bottom']>b[1]+0.5: continue
            col='word' if w['x0']<300 else ('m1' if w['x0']<428 else 'm2')
            cells.setdefault(n,{}).setdefault(col,[]).append((round(w['top']),w['x0'],w['text']))
        for n,d in cells.items():
            out={}
            for k,v in d.items():
                v.sort(); pos=[]; lines=[]
                for top,x,t in v:
                    m=re.match(POS,t)
                    if m: pos.append(m.group(1)); continue
                    if lines and abs(lines[-1][0]-top)<=3: lines[-1][1].append(t)
                    else: lines.append([top,[t]])
                txt=''
                for _,ts in lines:
                    seg=' '.join(undouble(t) for t in ts)
                    if txt and (len(seg.replace(' ',''))<=2 or re.search(r'(^| )[가-힣]$',txt) and not re.search(r'[된는은한의을를에로수할될등및]$',txt)): txt+=seg
                    else: txt=(txt+' '+seg).strip()
                m=re.match(r'^\((명|동|형|부)\(\1\)\s*\)\s*',txt)
                if m: pos=pos or [m.group(1)]; txt=txt[m.end():]
                out[k]=(pos[0] if pos else '',txt)
            rows[n]=out
over=json.load(open(sys.argv[3]))
res=[]
for n in sorted(rows):
    d=rows[n]
    if str(n) in over: res.append({"id":n,**over[str(n)]}); continue
    ms=[{"pos":d[c][0],"meaning":d[c][1]} for c in ('m1','m2') if c in d and d[c][1]]
    res.append({"id":n,"word":undouble(d.get('word',('',''))[1]),"meanings":ms})
json.dump(res,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
print(len(res))
