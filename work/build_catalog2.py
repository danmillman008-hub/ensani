import json, re, collections, sys

FA='۰۱۲۳۴۵۶۷۸۹'; AR='٠١٢٣٤٥٦٧٨٩'
def digits(s):
    for i,c in enumerate(FA): s=s.replace(c,str(i))
    for i,c in enumerate(AR): s=s.replace(c,str(i))
    return s
def unfold(cell):
    if cell is None: return ''
    units=re.findall(r'\d+|[^\d]', cell.replace('\n',' '))
    return ''.join(reversed(units))
def clean(s):
    s=digits(s).replace('\u200c',' ')
    s=re.sub(r'[A-Za-z]+',' ',s)
    return re.sub(r'\s+',' ',s).strip()

CODE_RE=re.compile(r'^\d{5}$')
KEEP_SEC=re.compile(r'(استان|مخصوص متقاضيان بومی|پيام نور|غیرانتفاعی|غيرانتفاعی)')

def parse_table(rec):
    rows=[[unfold(c) for c in r] for r in rec['rows']]
    ncols=len(rows[0]) if rows else 0
    out=[]; prev=None; buf=[]
    for r in rows:
        cells=[clean(c) for c in r]
        cidx=None
        for i,c in enumerate(cells):
            if CODE_RE.match(c): cidx=i
        if cidx is None:
            txt=' '.join(c for c in cells if len(c)>1 and not re.fullmatch(r'[\d\- ]+',c))
            if txt: buf.append(txt)
            continue
        code=cells[cidx]; title=cells[cidx-1] if cidx>=1 else ''
        pre=' '.join(buf); buf=[]
        title=re.sub(r'\s+',' ',(pre+' '+title)).strip()
        notes=[]; gender=[]; caps=[]; dore=''; nahve=''
        for i,c in enumerate(cells):
            if i==cidx or i==cidx-1 or not c: continue
            if c in ('مرد','زن','-','--'): gender.append(c); continue
            if re.fullmatch(r'\d{1,4}', c): caps.append(int(c)); continue
            if 'آزمون' in c or 'سوابق' in c: nahve=c; continue
            if any(k in c for k in ['روزانه','نوبت','پردیس','مجازی','غيردولتي','شهريه','محروم','فرهنگيان','بورسيه','دانشجو']):
                dore=(dore+' '+c).strip(); continue
            notes.append(c)
        row={'code':code,'title':title,'dore':dore,'nahve':nahve,'gender':gender,
             'caps':caps,'notes':' '.join(notes),'ncols':ncols,'section':rec['section'],
             'file':rec['file'],'page':rec['page']}
        out.append(row); prev=row
    return out

SEC_RE=re.compile(r'استان\s+(.+?)\s*-\s*(.+?)(?:\s*-\s*([^\-\n]+))?$')
def parse_section(sec):
    s=re.sub(r'^ادامه\s+','',sec).strip()
    m=re.search(r'استان\s+([^\-\n]+?)\s*-\s*(.+)$', s)
    if m:
        prov=m.group(1).strip(); rest=m.group(2).strip()
        city=''
        m2=re.match(r'(.+?)\s*-\s*([^\-\n]+)$', rest)
        if m2 and len(m2.group(2))<20 and 'محل' not in m2.group(2):
            rest=m2.group(1).strip(); city=m2.group(2).strip()
        return prov, rest, city
    if 'پيام نور' in s:
        m3=re.search(r'پيام نور\s+استان\s+([^\-\n]+?)\s*-\s*(.+)$', s)
        if m3: return m3.group(1).strip(), s, m3.group(2).strip()
    return '', s, ''

def main(inp, outp):
    recs=[json.loads(l) for l in open(inp)]
    rows=[]
    for rec in recs:
        for r in parse_table(rec):
            prov,inst,city=parse_section(r['section'])
            r['province']=prov; r['institution']=inst; r['city']=city
            rows.append(r)
    # filter junk: require a plausible section
    good=[r for r in rows if KEEP_SEC.search(r['section']) and len(r['title'])>=3]
    print('total rows', len(rows), 'after filter', len(good))
    cc=collections.Counter(r['code'] for r in good)
    print('unique codes', len(cc), 'dups', [c for c,n in cc.items() if n>1][:20])
    with open(outp,'w') as f:
        for r in good: f.write(json.dumps(r, ensure_ascii=False)+'\n')

main(sys.argv[1], sys.argv[2])
