import json, re, sys, pymupdf

def main(fnames, outpath):
    out = open(outpath, 'w')
    for fname in fnames:
        doc = pymupdf.open(fname)
        for pno in range(doc.page_count):
            page = doc[pno]
            try:
                tabs = page.find_tables()
            except Exception as e:
                print('ERR', fname, pno, e, file=sys.stderr); continue
            if not tabs.tables: continue
            blocks = page.get_text('blocks')
            for t in tabs.tables:
                x0,y0,x1,y1 = t.bbox
                sec=''; best_y=-1
                for b in blocks:
                    bx0,by0,bx1,by1,txt,bn,bt = b
                    if bt!=0: continue
                    if by1 <= y0+2 and 55 < by0 < 800:
                        clean=' '.join(txt.split())
                        if not clean or 'دفترچه راهنماي' in clean: continue
                        if by0 > best_y: best_y=by0; sec=clean
                rows=[[('' if c is None else c) for c in r] for r in t.extract()]
                out.write(json.dumps({'file':fname,'page':pno,'section':sec,
                    'bbox':[round(v,1) for v in t.bbox],'rows':rows}, ensure_ascii=False)+'\n')
        doc.close()
        print('done', fname, file=sys.stderr)
    out.close()

if __name__=='__main__':
    main(sys.argv[2:], sys.argv[1])
