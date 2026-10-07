# -*- coding: utf-8 -*-
"""Build the final 150-choice list with acceptance-chance estimates."""
import json, re, unicodedata, collections, math, csv

rows=[json.loads(l) for l in open('work/catalog_1405.jsonl')]

REPAIR={'عالمه':'علامه','اسالمشهر':'اسلامشهر','مالرد':'ملارد','اسالمی':'اسلامی',
        'سالمت':'سلامت','طال':'طلا','السالم':'السلام','مالياتي':'مالیاتی','اسالم':'اسلام',
        'ااسلمی':'اسلامی','ااسلمشهر':'اسلامشهر','سالمان':'سالمان','عالمی':'عالمی'}
def fix_display(s):
    s=re.sub(r'[A-Za-z]','',s)
    for k,v in REPAIR.items(): s=s.replace(k,v)
    s=s.replace(')(','(').replace(') (','(')
    s=re.sub(r'\s+',' ',s).strip()
    s=s.replace('i','').replace('w','').replace('n','').replace('o','').replace('r','')
    return s.strip()
def canon(s):
    s=s.replace('ي','ی').replace('ك','ک').replace('آ','ا').replace('أ','ا').replace('إ','ا')
    s=s.replace('ة','ه').replace('ۀ','ه').replace('ؤ','و').replace('ئ','ی').replace('\u200c',' ')
    s=s.replace('ال','*L').replace('لا','*L')
    s=re.sub(r'[().،:؛«»\-–_/\\\u0640]',' ',s)
    return re.sub(r'\s+',' ',s).strip()

TYPE_KEYS=[('پیام نور','پیامنور'),('غيرانتفاعی','غیرانتفاعی'),('غیرانتفاعی','غیرانتفاعی'),('مجازي','مجازی')]
CATS=[('مدیریت',['مدیریت','کارافرینی']),('حقوق',['حقوق','فقه','قضا']),
      ('روانشناسی/مشاوره',['روان','مشاور','امور تربیتی']),('مالی/حسابداری/اقتصاد',['حسابداری','مالی','بانکداری','بیمه','اقتصاد'])]
def category(title):
    ct=canon(title)
    for k,keys in CATS:
        if any(x in ct for x in keys): return k
    return None
def itype(r):
    s=canon(r['institution'])+' '+canon(r['section'])
    if 'پيام نور' in s or 'پیام نور' in s: return 'پیامنور'
    if 'غيرانتفاعی' in s or 'غیرانتفاعی' in s or 'موسسه' in s or 'مؤسسه' in s: return 'غیرانتفاعی'
    return 'دولتی'
def city_group(r):
    cp=canon(r['province']); ci=canon(r['institution'])+' '+canon(r['city'])+' '+canon(r['section'])
    if cp=='*L*برز' or 'کرج' in ci and cp!='*L*برز' and False: return 'کرج'
    if cp=='*L*برز': return 'کرج'
    if cp=='تهران': return 'تهران'
    if cp=='قزوین': return 'قزوین'
    if cp=='اذربایجان شرقی' and ('تبريز' in ci or 'تبریز' in ci or 'سهند' in ci): return 'تبریز'
    if cp=='اذربایجان شرقی': return 'آذربایجان شرقی (غیر تبریز)'
    return cp
# ---- candidate pool ----
pool=[]
for r in rows:
    cat=category(r['title'])
    if not cat: continue
    if 'محروم' in r['section']: continue
    g=''.join(r['gender'])
    if 'زن' not in (g or 'زن'): continue
    t=fix_display(r['title']); inst=fix_display(r['institution'])
    if len(t)<3 or 'کدرشته محل خدمت' in t or 'ظرفيت جنس' in t: continue
    ty=itype(r)
    dore=r['dore'] or ('پیامنور' if ty=='پیامنور' else ('غیرانتفاعی' if ty=='غیرانتفاعی' else ''))
    if 'مجازي' in canon(r['notes']) or 'مجازی' in dore: dore='مجازی (غیرانتفاعی)'
    pool.append(dict(code=r['code'],title=t,inst=inst,province=r['province'],city=r['city'],
                     section=fix_display(r['section']),cat=cat,ctype=ty,dore=fix_display(dore).strip(' -'),
                     nahve=r['nahve'],cap=sum(r['caps']),notes=fix_display(r['notes'])[:80],
                     cg=city_group(r)))
print('pool size:', len(pool))
json.dump(pool, open('work/pool.json','w'), ensure_ascii=False)
cc=collections.Counter((p['ctype'],p['cat']) for p in pool)
for k,v in sorted(cc.items()): print('   ',k,v)
print('cities:', collections.Counter(p['cg'] for p in pool).most_common(12))
