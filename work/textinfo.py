# -*- coding: utf-8 -*-
"""استخراج عنوان و توضیحات تمیز برای کدهای انتخابی از لایه متنی دفترچه‌ها"""
import re, json, sys, os
FA='۰۱۲۳۴۵۶۷۸۹'
def norm(s):
    for i,d in enumerate(FA): s=s.replace(d,str(i))
    return s
FILES={
 '14050712psczi27719_0001.pdf':'work/txt/14050712psczi27719_0001.txt',
 '14050712psczi27719_0002.pdf':'work/txt/14050712psczi27719_0002.txt',
 '14050712psczi27719_0003.pdf':'work/txt/14050712psczi27719_0003.txt',
}
NOTE_RE=re.compile(r'(خوابگاه|محدوديت|مختص|مصاحبه|محل تحصيل|پيوست|شهريه|پرديس|اسكان|بومي|شرايطي|فاقد)')
def clean(l): return re.sub(r'\s+',' ',norm(l)).strip()
def extract(code, idx):
    """idx = {code: (file,page,lineindex)} prebuilt"""
    f,p,i = idx[code]
    lines=[clean(l) for l in FILES[f].split('<<<PAGEBREAK>>>')[0]] if False else None
    return None
def build_index():
    idx={}
    for f,path in FILES.items():
        pages=open(path, encoding='utf-8').read().split('<<<PAGEBREAK>>>')
        for pno,page in enumerate(pages):
            for i,l in enumerate(page.split('\n')):
                for m in re.finditer(r'\b(\d{4,6})\b', norm(l)):
                    idx.setdefault(m.group(1), (f,pno,i))
    return idx
IDX=None
def info(code):
    global IDX
    if IDX is None: IDX=build_index()
    if code not in IDX: return None
    f,p,i = IDX[code]
    pages=open(FILES[f], encoding='utf-8').read().split('<<<PAGEBREAK>>>')
    raw=[clean(l) for l in pages[p].split('\n')]
    line=raw[i]
    code_pos=line.find(code)
    pre=line[:code_pos].strip()
    post=line[code_pos+len(code):].strip()
    title_parts=[]
    # اگر عنوان روی همان خط قبل از کد باشد
    if pre and not re.fullmatch(r'[\d\s\-–]+', pre):
        title_parts.append(pre)
    j=i-1
    guard=0
    while j>=0 and guard<4:
        c=raw[j]
        if not c: j-=1; guard+=1; continue
        if re.fullmatch(r'[\d\s\-–,]+', c): break
        if re.fullmatch(r'(مرد|زن|مرد زن|مرد-|زن-|مرد زن-|-)+', c): break
        title_parts.insert(0,c); j-=1; guard+=1
    title=' '.join(title_parts)
    title=re.sub(r'^[\d\s\-–]+','',title)
    title=re.sub(r'[\d\s\-–]+$','',title).strip()
    # یادداشت‌ها: بالاتر از نقطه توقف
    notes=[]
    k=j if j>=0 else i-1
    while k>=0 and len(notes)<5:
        c=raw[k]
        if not c: k-=1; continue
        if NOTE_RE.search(c):
            notes.insert(0,c); k-=1; continue
        if re.fullmatch(r'[\d\s\-–,]+', c) or c in ('مرد','زن','مرد زن','مرد-','زن-','-'): k-=1; continue
        break
    notes=' '.join(notes)
    notes=re.sub(r'(مرد زن|مرد|زن|-)+$','',notes).strip(' -')
    return dict(code=code,title=title,notes=notes,dore_nahve=post,file=f[-8:],page=p+1)
if __name__=='__main__':
    tests=sys.argv[1:] or ['35974','35985','34637','36427','37623','37530','12434','10148','36314','37402']
    for c in tests:
        print(c, json.dumps(info(c), ensure_ascii=False))
