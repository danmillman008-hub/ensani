import json, re, collections, sys

FA='۰۱۲۳۴۵۶۷۸۹'; AR='٠١٢٣٤٥٦٧٨٩'
def digits(s):
    for i,c in enumerate(FA): s=s.replace(c,str(i))
    for i,c in enumerate(AR): s=s.replace(c,str(i))
    return s

def unfold(cell):
    """PDF stores letters in visual (reversed) order but keeps digit runs atomic."""
    if cell is None: return ''
    s=cell.replace('\n',' ')
    units=re.findall(r'\d+|[^\d]', s)
    return ''.join(reversed(units))

def clean(s):
    s=digits(s)
    s=s.replace('\u200c',' ')
    # drop latin junk (watermark fragments)
    s=re.sub(r'[A-Za-z]+',' ',s)
    s=re.sub(r'\s+',' ',s)
    return s.strip()

LIG=re.compile(r'ال|لا')
def canon(s):
    """canonical form for matching: unify yeh/kaf, treat ال/لا as one token"""
    s=clean(s)
    s=s.replace('ي','ی').replace('ك','ک').replace('ۀ','ه').replace('ة','ه')
    s=re.sub(r'[أإآ]','ا',s); s=s.replace('ؤ','و').replace('ئ','ی')
    s=s.replace('ال','*L').replace('لا','*L')
    s=re.sub(r'[().،:؛«»\-–_/\\]',' ',s)
    s=re.sub(r'\s+',' ',s)
    return s.strip()

CODE_RE=re.compile(r'^\d{5}$')

def parse_table(rec):
    """Yield dicts for each data row of a table record."""
    rows=[[unfold(c) for c in r] for r in rec['rows']]
    ncols=len(rows[0]) if rows else 0
    out=[]
    prev=None
    for r in rows:
        cells=[clean(c) for c in r]
        cidx=None
        for i,c in enumerate(cells):
            if CODE_RE.match(c): cidx=i
        if cidx is None:
            # continuation line: append raw text to previous row notes
            txt=' '.join(x for x in cells if x and not re.fullmatch(r'\d{1,2}',x))
            if prev is not None and len(txt)>2:
                prev['notes']=clean(prev['notes']+' '+txt)
            continue
        code=cells[cidx]
        title=cells[cidx-1] if cidx>=1 else ''
        # scan other cells
        notes=[]; gender=[]; caps=[]; dore=''; nahve=''
        for i,c in enumerate(cells):
            if i==cidx or i==cidx-1 or not c: continue
            if c in ('مرد','زن','-','--'): gender.append(c); continue
            if re.fullmatch(r'\d{1,4}', c): caps.append(int(c)); continue
            if 'آزمون' in c or 'سوابق' in c: nahve=c; continue
            if any(k in c for k in ['روزانه','نوبت','پردیس','مجازی','غيردولتي','شهريه','محروم','فرهنگيان','بورسيه','دانشجو- معلم','معلم']):
                dore=c if not dore else dore+' '+c; continue
            notes.append(c)
        row={'code':code,'title':title,'dore':dore,'nahve':nahve,
             'gender':gender,'caps':caps,'notes':' '.join(notes),
             'ncols':ncols,'section':rec['section'],'file':rec['file'],'page':rec['page']}
        out.append(row); prev=row
    return out

def main(inp, outp):
    recs=[json.loads(l) for l in open(inp)]
    all_rows=[]
    for rec in recs:
        all_rows.extend(parse_table(rec))
    with open(outp,'w') as f:
        for r in all_rows:
            f.write(json.dumps(r, ensure_ascii=False)+'\n')
    print('rows:', len(all_rows))
    cc=collections.Counter(r['code'] for r in all_rows)
    dup=[c for c,n in cc.items() if n>1]
    print('codes:', len(cc), 'dups:', len(dup), dup[:10])

main(sys.argv[1], sys.argv[2])
