# -*- coding: utf-8 -*-
import json, math, collections, csv, re
pool=json.load(open('work/pool_scored.json'))
def n(s):
    s=s.replace('ي','ی').replace('ك','ک').replace('آ','ا').replace('\u200c',' ')
    s=s.replace('ال','*L').replace('لا','*L')
    return re.sub(r'[().،:؛«»\-–_/\\]',' ',s)
JUNK=['دفترچه','پيوست','جنس','ظرفيت','کدرشته','توضيحات','مرد','زن','معرفي','خوابگاه','ممنوعيت',
      'شرايط','فاقد','محل تحصيل','ادامه','رشته متعلق','کاردانی','کارداني']
BAD_FIELD=['مدیریت اموزشی','مدیریت اموزش','مدیریت فرهنگی','مدیریت ورزشی','علوم ورزشی','ورزشی',
           'مهندسی','کشاورزی','علوم دامی','صنایع غذایی','زیست','شیمی','فیزیک','ریاضی','امار','آمار',
           'کارشناسی ارشد','شافعی','اهل سنت','معارف','بهیاری','کاردانی']
def bad(t):
    x=n(t)
    if any(j in x for j in (n(j) for j in JUNK)): return True
    if any(b in x for b in (n(b) for b in BAD_FIELD)): return True
    return len(t)<3
PREF_CITY=['کرج','تهران','قزوین','تبریز']
TIER1=['تهران','شهید بهشتی','علامه','فردوسی','تبریز','اصفهان','شیراز','خوارزمی','الزهرا','شاهد','توانبخشی','امام خمینی','شهید مدنی','مازندران','علوم قضایی']
TIER2=['گیلان','زنجان','لرستان','هرمزگان','کردستان','ارومیه','شاهرود','سمنان','کاشان','شهید باهنر','یزد',
       'ولی عصر','رازی','اراک','شهرکرد','بوعلی','شهید چمران','محقق اردبیلی','صنعتی سهند','بیرجند','گلستان','بجنورد','میبد','قم']
def tier(p):
    inst=n(p['inst'])
    for k in TIER1:
        if n(k) in inst: return 1
    for k in TIER2:
        if n(k) in inst: return 2
    return 3
def cat_rank(p):
    return CAT_ORDER[p["cat"]]
CAT_ORDER={'مدیریت':0,'حقوق':1,'روانشناسی/مشاوره':2,'مالی/حسابداری/اقتصاد':3}
def mgmt_rank(t):
    x=n(t)
    for i,k in enumerate(['مالی','بازرگانی','کسب و کار','کارافرینی','بیمه','گمرک','بانک','تجارت','صنعتی','دولتی','گردشگری','هتلداری','بازاریابی']):
        if n(k) in x: return i
    return 9
DISPLAY=[('دانشگاه بين المللی ) امام خمينی (ره','دانشگاه بین‌المللی امام خمینی(ره)'),
   ('دانشگاه بين المللي ) امام خميني (ره','دانشگاه بین‌المللی امام خمینی(ره)'),
   (')دانشگاه الزهرا (س(ويژه خواهران– تهران','دانشگاه الزهرا(س) – ویژه خواهران'),
   (')دانشگاه الزهرا (س(ويژه خواهران – تهران','دانشگاه الزهرا(س) – ویژه خواهران'),
   (')دانشگاه الزهرا (س(','دانشگاه الزهرا(س)'),
   ('دانشگاه بين المللی ) امام خمينی (ره','دانشگاه بین‌المللی امام خمینی(ره)')]
def disp(s):
    for k,v in DISPLAY:
        s=s.replace(k,v)
    s=s.replace('(محل تحصيل تهران)','(محل تحصیل تهران)').replace('')  if False else s
    s=re.sub(r'\s+',' ',s).strip(' )(')
    s=s.replace('ي','ی').replace('ك','ک')
    return s
def city_disp(p):
    if p.get('cg') in PREF_CITY: return p['cg']
    if p.get('cg'): return p['cg'].replace('*L','لا')
    pr=p['province'].replace('*L','لا').replace('ا*Lم','ایلام').replace('گی*Lن','گیلان')
    return pr if pr else '—'
cands=[p for p in pool if not bad(p['title'])]
seen=set(); L=[]
def add(p, block, note=''):
    if p['code'] in seen: return False
    seen.add(p['code']); L.append({**p,'block':block,'note':note or p['notes']}); return True
# B1
b1=[p for p in cands if p['ctype']=='دولتی' and p['nahve']=='با آزمون' and p['cg'] in PREF_CITY and 'نوبت دوم' not in p['dore']]
q={'مدیریت':4,'حقوق':3,'روانشناسی/مشاوره':3,'مالی/حسابداری/اقتصاد':2}
for cat,quota in q.items():
    sub=[p for p in b1 if p['cat']==cat]
    sub.sort(key=lambda p:(tier(p), mgmt_rank(p['title']) if cat=='مدیریت' else 0, -p['p']))
    k=0
    for p in sub:
        if k>=quota: break
        if add(p,'B1'): k+=1
# B2
b2=[p for p in cands if p['ctype']=='دولتی' and ('نوبت دوم' in p['dore'] or 'خودگردان' in p['notes']) and p['cg'] in PREF_CITY]
b2.sort(key=lambda p:(cat_rank(p) if False else -p['p']))
k=0
for p in b2:
    if k>=10: break
    if add(p,'B2'): k+=1
# B3 فرهنگیان البرز
FAR=[('49112','راهنمایی و مشاوره','دانشگاه فرهنگیان – پردیس بنت‌الهدی صدر قزوین (محل خدمت: کرج ناحیه ۱)'),
     ('49113','راهنمایی و مشاوره','دانشگاه فرهنگیان – پردیس بنت‌الهدی صدر قزوین (کرج ناحیه ۲)'),
     ('49114','راهنمایی و مشاوره','دانشگاه فرهنگیان – پردیس بنت‌الهدی صدر قزوین (کرج ناحیه ۳)'),
     ('49115','راهنمایی و مشاوره','دانشگاه فرهنگیان – پردیس بنت‌الهدی صدر قزوین (کرج ناحیه ۴)'),
     ('49116','راهنمایی و مشاوره','دانشگاه فرهنگیان – پردیس بنت‌الهدی صدر قزوین (چهارباغ)'),
     ('49117','راهنمایی و مشاوره','دانشگاه فرهنگیان – پردیس بنت‌الهدی صدر قزوین (ساوجبلاغ)'),
     ('49237','راهنمایی و مشاوره','دانشگاه فرهنگیان – البرز (ظرفیت تکمیلی)'),
     ('49238','راهنمایی و مشاوره','دانشگاه فرهنگیان – البرز (ظرفیت تکمیلی)'),
     ('49112ب','','')]
for code,title,inst in [x for x in FAR if x[0]!='49112ب']:
    if code in seen: continue
    seen.add(code)
    L.append(dict(code=code,title=title,inst=inst,city='کرج',province='البرز',cat='فرهنگیان',
        ctype='فرهنگیان',dore='روزانه (فرهنگیان)',nahve='پذیرش آزمون اختصاصی دانشجو-معلم',
        cap=0,notes='تعهد خدمت در استان البرز – فقط اگر در آزمون دانشجو-معلم «مجاز» شده باشید',
        p=None,ref=None,why='ملاک پذیرش: آزمون اختصاصی دانشجو-معلم (جدا از رتبه سراسری)',block='B3'))
for code,title,inst in [('49089','آموزش علوم اجتماعی','دانشگاه فرهنگیان – پردیس امیرکبیر کرج'),
                        ('49088','آموزش علوم اجتماعی','دانشگاه فرهنگیان – پردیس امیرکبیر کرج'),
                        ('49090','آموزش علوم اجتماعی','دانشگاه فرهنگیان – پردیس امیرکبیر کرج'),
                        ('49091','آموزش علوم اجتماعی','دانشگاه فرهنگیان – پردیس امیرکبیر کرج'),
                        ('49101','امور تربیتی','دانشگاه فرهنگیان – پردیس حضرت معصومه قم (محل خدمت کرج)')]:
    if code in seen: continue
    seen.add(code)
    L.append(dict(code=code,title=title,inst=inst,city='کرج',province='البرز',cat='فرهنگیان',
        ctype='فرهنگیان',dore='روزانه (فرهنگیان)',nahve='پذیرش آزمون اختصاصی دانشجو-معلم',
        cap=0,notes='تعهد خدمت – فقط در صورت «مجاز» شدن در آزمون دانشجو-معلم',
        p=None,ref=None,why='ملاک پذیرش: آزمون اختصاصی دانشجو-معلم',block='B3'))
# B4
b4=[p for p in cands if p['ctype']=='دولتی' and p['nahve']=='با آزمون' and p['cg'] not in PREF_CITY
    and p['cg'] and 'نوبت دوم' not in p['dore'] and 'خودگردان' not in p['notes'] and p['p']>=25]
b4.sort(key=lambda p:(tier(p), cat_rank(p), mgmt_rank(p['title']) if p['cat']=='مدیریت' else 0, -p['p']))
k=0
for p in b4:
    if k>=34: break
    if add(p,'B4'): k+=1
# B5
b5=[p for p in cands if p['ctype']=='دولتی' and ('نوبت دوم' in p['dore'] or 'خودگردان' in p['notes'])
    and p['cg'] not in PREF_CITY and p['cg'] and p['p']>=30]
b5.sort(key=lambda p:(-p['p'], tier(p), cat_rank(p)))
k=0
for p in b5:
    if k>=14: break
    if add(p,'B5'): k+=1
# B6
b6=[p for p in cands if p['ctype']=='غیرانتفاعی' and p['cg'] in PREF_CITY and p['nahve']=='با آزمون']
b6.sort(key=lambda p:(-p['p'], cat_rank(p), mgmt_rank(p['title'])))
k=0
for p in b6:
    if k>=18: break
    if add(p,'B6'): k+=1
# B7
b7=[p for p in cands if p['ctype']=='غیرانتفاعی' and p['cg'] in PREF_CITY and p['nahve']!='با آزمون']
b7.sort(key=lambda p:(cat_rank(p), mgmt_rank(p['title']) if p['cat']=='مدیریت' else 0, -p['cap']))
k=0
for p in b7:
    if k>=20: break
    if add(p,'B7'): k+=1
# B8
b8=[p for p in cands if p['ctype']=='پیامنور' and p['cg'] in PREF_CITY]
b8.sort(key=lambda p:(cat_rank(p), mgmt_rank(p['title']) if p['cat']=='مدیریت' else 0, -p['cap']))
k=0
for p in b8:
    if k>=18: break
    if add(p,'B8'): k+=1
# B9
b9=[p for p in cands if p['ctype'] in ('پیامنور','غیرانتفاعی') and p['cg'] not in PREF_CITY]
b9.sort(key=lambda p:(cat_rank(p), mgmt_rank(p['title']) if p['cat']=='مدیریت' else 0, -p['cap']))
k=0
for p in b9:
    if k>=10: break
    if add(p,'B9'): k+=1
print('TOTAL', len(L), collections.Counter(x['block'] for x in L))
json.dump(L, open('work/list150.json','w'), ensure_ascii=False, indent=1)
for i,x in enumerate(L,1):
    print(f"{i:3d} {x['block']} {x['code']} | {disp(x['title'])[:24]:26s}| {disp(x['inst'])[:36]:38s}| {city_disp(x)[:12]:12s}| {x['dore'][:10]:10s}| {x['nahve'][:18]:18s}| cap{x['cap']:>3} | ref{x['ref'] if x['ref'] is not None else '-':>6} | p{x['p'] if x['p'] is not None else '-':>3}")
