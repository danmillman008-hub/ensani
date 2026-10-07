import json, re, collections, sys
rows=[json.loads(l) for l in open('work/catalog_1405.jsonl')]
def canon(s):
    s=s.replace('ي','ی').replace('ك','ک').replace('آ','ا').replace('أ','ا').replace('إ','ا')
    s=s.replace('ة','ه').replace('ۀ','ه').replace('ؤ','و').replace('ئ','ی').replace('\u200c',' ')
    s=s.replace('ال','*L').replace('لا','*L')
    s=re.sub(r'[().،:؛«»\-–_/\\\u0640]',' ',s)
    return re.sub(r'\s+',' ',s).strip()
for r in rows:
    r['ct']=canon(r['title']); r['ci']=canon(r['institution']); r['cn']=canon(r['notes']); r['cp']=canon(r['province']); r['cc']=canon(r['city']); r['cs']=canon(r['section'])

CATS=[('مدیریت',['مدیریت','کارافرینی']),
      ('حقوق',['حقوق','فقه','قضا','قضایی']),
      ('روانشناسی',['روان','مشاور']),
      ('مالی/حسابداری/اقتصاد',['حسابداری','مالی','بانکداری','بیمه','اقتصاد'])]
def cats(r):
    out=[]
    for k,keys in CATS:
        if any(x in r['ct'] for x in keys): out.append(k)
    return out
PROV=['تهران','*L*برز','قزوین','اذربایجان شرقی']
def city_grp(r):
    s=' '.join([r['ci'],r['cs'],r['notes']])
    p=r['cp']
    if p=='تهران': return 'تهران'
    if p=='*L*برز': return 'کرج'
    if p=='قزوین': return 'قزوین'
    if p=='اذربایجان شرقی': return 'تبریز'
    return ''
sel=[r for r in rows if cats(r) and 'محروم' not in r['section'] and not (r['gender'] and 'زن' not in r['gender'])]
print('candidates in target majors (all provinces):', len(sel))
tg=[r for r in sel if city_grp(r)]
print('in 4 target cities:', len(tg))
print(collections.Counter(city_grp(r) for r in tg))
print()
for city in ['کرج','تهران','قزوین','تبریز']:
    print('#'*90); print('###', city)
    sub=[r for r in tg if city_grp(r)==city]
    for r in sorted(sub, key=lambda x:(cats(x)[0], x['ct'], x['code'])):
        inst=r['institution'][:52]
        print(f"{r['code']} | {r['title'][:30]:32s} | {inst:54s} | {r['dore'][:12]:12s} | {r['nahve'][:22]:22s} | g={''.join(r['gender'])[:6]:6s} | cap={sum(r['caps']):>3} | {r['notes'][:45]}")
