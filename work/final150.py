# -*- coding: utf-8 -*-
"""لیست نهایی ۱۵۰ کدرشته — ترکیب باآزمون و سوابق‌محور، مرتب‌شده به ترتیب اولویت پیشنهادی فرم"""
import json, re, collections, math
pool=json.load(open('work/pool_scored.json'))
def n(s):
    s=s.replace('ي','ی').replace('ك','ک').replace('آ','ا').replace('\u200c',' ')
    s=s.replace('ال','*L').replace('لا','*L')
    return re.sub(r'[().،:؛«»\-–_/\\]',' ',s)
JUNK=['دفترچه','پيوست','پیوست','جنس','ظرفيت','ظرفیت','کدرشته','توضيحات','معرفي','معرفی','خوابگاه',
      'ممنوعيت','شرايط','شرایط','فاقد','ادامه','رشته متعلق','کاردانی','کارداني','سال دوم','ملكي','ملکی','عملکرد']
BADF=['مدیریت اموزش','مدیریت فرهنگی','مدیریت ورزشی','علوم ورزشی','ورزشی','مهندسی','کشاورزی','علوم دامی',
      'صنایع غذایی','زیست','شیمی','فیزیک','ریاضی','آمار','امار','کارشناسی ارشد','شافعی','اهل سنت','معارف',
      'بهیاری','پزشکی','پرستاری','خرما','علوم پزشکی','دامپزشکی','هتلداری','اقتصاد کشاورزی']
def bad(t):
    x=n(t)
    if any(n(j) in x for j in JUNK): return True
    if any(n(b) in x for b in BADF): return True
    return len(t)<3
PREF=['کرج','تهران','قزوین','تبریز']
def cg(p):
    c=p.get('cg') or ''
    return 'کرج' if c=='البرز' else c
CATQ={'مدیریت':0,'حقوق':1,'روانشناسی/مشاوره':2,'مالی/حسابداری/اقتصاد':3}
CITYQ=['تهران','الزهرا','علامه','خوارزمی','شهید بهشتی','شاهد',
       'مشهد','فردوسی','شیراز','اصفهان','تبریز','قزوین','امام خمینی','رشت','گیلان','کرمانشاه','رازی',
       'ارومیه','یزد','کرمان','باهنر','اهواز','چمران','قم','معصومه','مازندران','زنجان',
       'همدان','کردستان','اراک','بیرجند','بجنورد','گلستان','سبزوار','کاشان','سمنان','شاهرود']
def cityq(p):
    s=n(p['inst'])
    for i,k in enumerate(CITYQ):
        if n(k) in s: return i
    return 99
def mgr(t):
    x=n(t)
    for i,k in enumerate(['مالی','بازرگانی','کسب و کار','کارآفرینی','کارافرینی','بیمه','گمرک','بانک','تجارت','صنعتی','دولتی','گردشگری','بازاریابی']):
        if n(k) in x: return i
    return 9
def ok150(p): return not bad(p['title'])
withA=[p for p in pool if ok150(p) and p['nahve']=='با آزمون']
savab=[p for p in pool if ok150(p) and p['nahve']=='صرفا با سوابق تحصيلي' and cg(p) in PREF]
seen=set(); L=[]
def add(p,block,note=''):
    if p['code'] in seen: return False
    seen.add(p['code'])
    L.append(dict(code=p['code'],title=p['title'],inst=p['inst'],city=p.get('cg') or p.get('province',''),
                  cat=p['cat'],ctype=p['ctype'],dore=p['dore'],nahve=p['nahve'],cap=p['cap'],p=p['p'],
                  ref=p['ref'],why=p['why'],block=block,note=note)); return True
def take(lst,quota,block,key,note=''):
    k=0
    for p in sorted(lst,key=key):
        if k>=quota: break
        if add(p,block,note): k+=1
# B1
b1=[p for p in withA if p['ctype']=='دولتی' and cg(p) in PREF and 'نوبت دوم' not in p['dore']]
for cat,q in [('مدیریت',4),('حقوق',3),('روانشناسی/مشاوره',3),('مالی/حسابداری/اقتصاد',2)]:
    sub=[p for p in b1 if p['cat']==cat]
    take(sub,q,'B1',lambda p:(0 if cg(p)=='تهران' else 1, mgr(p['title']) if cat=='مدیریت' else 0, p['p']))
# B2
b2=[p for p in withA if p['ctype']=='دولتی' and cg(p) in PREF and ('نوبت دوم' in p['dore'] or 'خودگردان' in (p.get('notes') or ''))]
take(b2,10,'B2',lambda p:(CATQ[p['cat']],p['p']))
# B3 فرهنگیان البرز (دختران) — محل خدمت‌های استان البرز
FAR=[('49113','راهنمایی و مشاوره','کرج ناحیه ۲','پردیس بنت‌الهدی صدر قزوین',2),
     ('49114','راهنمایی و مشاوره','کرج ناحیه ۳','پردیس بنت‌الهدی صدر قزوین',2),
     ('49115','راهنمایی و مشاوره','کرج ناحیه ۴','پردیس بنت‌الهدی صدر قزوین',2),
     ('49112','راهنمایی و مشاوره','کرج ناحیه ۱','پردیس بنت‌الهدی صدر قزوین',1),
     ('49116','راهنمایی و مشاوره','چهارباغ','پردیس بنت‌الهدی صدر قزوین',1),
     ('49117','راهنمایی و مشاوره','ساوجبلاغ','پردیس بنت‌الهدی صدر قزوین',1),
     ('49118','راهنمایی و مشاوره','نظرآباد','پردیس بنت‌الهدی صدر قزوین',1),
     ('49088','آموزش علوم اجتماعی','کرج ناحیه ۲','پردیس امیرکبیر کرج',1),
     ('49089','آموزش علوم اجتماعی','کرج ناحیه ۳','پردیس امیرکبیر کرج',1),
     ('49090','آموزش علوم اجتماعی','کرج ناحیه ۴','پردیس امیرکبیر کرج',1),
     ('49091','آموزش علوم اجتماعی','ساوجبلاغ','پردیس امیرکبیر کرج',1),
     ('49102','امور تربیتی','کرج ناحیه ۴','پردیس حضرت معصومه قم',3),
     ('49104','امور تربیتی','ساوجبلاغ','پردیس حضرت معصومه قم',2)]
for code,title,mahal,campus,cap in FAR:
    if code in seen: continue
    seen.add(code)
    L.append(dict(code=code,title=f'{title} (محل خدمت: {mahal})',inst=f'دانشگاه فرهنگیان – {campus}',
        city='کرج',cat='فرهنگیان',ctype='دانشجو-معلم',dore='روزانه – فرهنگیان',
        nahve='آزمون اختصاصی دانشجو-معلم',cap=cap,p=None,ref=None,
        why='وابسته به آزمون اختصاصی دانشجو-معلم (شرط: نمره کل و اختصاصی ≥ ۵۰۰۰)',block='B3',
        note='مخصوص متقاضیان بومی استان البرز (اولویت با بومی شهرستان‌های کرج/فردیس/چهارباغ) – تعهد خدمت'))
# B4
b4=[p for p in withA if p['ctype']=='دولتی' and cg(p) not in PREF and cg(p) and 'نوبت دوم' not in p['dore'] and 'خودگردان' not in (p.get('notes') or '')]
take(b4,30,'B4',lambda p:(cityq(p),CATQ[p['cat']],p['p']))
# B5
b5=[p for p in withA if p['ctype']=='دولتی' and cg(p) not in PREF and ('نوبت دوم' in p['dore'] or 'خودگردان' in (p.get('notes') or ''))]
take(b5,12,'B5',lambda p:(cityq(p),CATQ[p['cat']],p['p']))
# B6 غیرانتفاعی با آزمون – تهران/قم/مشهد
b6=[p for p in withA if p['ctype']=='غیرانتفاعی' and cg(p) in ('تهران',)]
for cat,q in [('مدیریت',8),('حقوق',6),('روانشناسی/مشاوره',5),('مالی/حسابداری/اقتصاد',5)]:
    sub=[p for p in b6 if p['cat']==cat]
    take(sub,q,'B6',lambda p:(-p['p'], mgr(p['title']) if cat=='مدیریت' else 0))
# B7 غیرانتفاعی با آزمون سایر شهرها
take([p for p in withA if p['ctype']=='غیرانتفاعی' and cg(p)!='تهران'],8,'B7',lambda p:(CATQ[p['cat']],-p['p']))
# B8 پیام‌نور با آزمون
b8=[p for p in withA if p['ctype']=='پیامنور']
take(b8,16,'B8',lambda p:(0 if cg(p) in PREF else 1,CATQ[p['cat']],-p['cap']))
# B9 ذخیره مطمئن: دولتی روزانه سایر شهرها با شانس بالا
b9=[p for p in withA if p['ctype']=='دولتی' and cg(p) not in PREF and 'نوبت دوم' not in p['dore'] and p['p']>=45]
take(b9,17,'B9',lambda p:(CATQ[p['cat']],-p['p'],cityq(p)))
# B10 ذخیره سوابق‌محور شهرهای ترجیحی
b10=sorted(savab,key=lambda p:(0 if cg(p)=='کرج' else 1 if cg(p)=='تهران' else 2, CATQ[p['cat']], -p['cap']))
take(b10,12,'B10',lambda p:(0 if cg(p)=='کرج' else 1 if cg(p)=='تهران' else 2, CATQ[p['cat']], -p['cap']),
     note='پذیرش صرفاً با سوابق تحصیلی (بدون آزمون) – در همان فرم ۱۵۰تایی قابل درج است')
print('TOTAL', len(L), collections.Counter(x['block'] for x in L))
json.dump(L, open('work/list150.json','w'), ensure_ascii=False, indent=1)
