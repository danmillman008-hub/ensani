#!/usr/bin/env python3
"""Extract all kod-reshte-mahal tables from 1405 booklet PDFs.

Outputs JSONL: one record per table row.
Each record: file, page, section (استان/مؤسسه header line), cells (list of str, RTL-normalized)
"""
import json
import re
import sys
import pymupdf

def norm_digits(s: str) -> str:
    fa = '۰۱۲۳۴۵۶۷۸۹'
    ar = '٠١٢٣٤٥٦٧٨٩'
    for i, c in enumerate(fa):
        s = s.replace(c, str(i))
    for i, c in enumerate(ar):
        s = s.replace(c, str(i))
    return s

ZWNJ = '\u200c'

def fix_rtl(s: str) -> str:
    """Table cells are extracted in visual (reversed) order; reverse back."""
    if s is None:
        return ''
    s = s.replace('\n', ' ')
    s = s.strip()
    # Reverse character order (string seems fully reversed incl. punctuation placement)
    s = s[::-1]
    s = re.sub(r'\s+', ' ', s)
    return norm_digits(s).strip()

def main(fnames, outpath):
    out = open(outpath, 'w')
    for fname in fnames:
        doc = pymupdf.open(fname)
        for pno in range(doc.page_count):
            page = doc[pno]
            try:
                tabs = page.find_tables()
            except Exception as e:
                print(f'!! find_tables fail {fname} p{pno}: {e}', file=sys.stderr)
                continue
            if not tabs.tables:
                continue
            blocks = page.get_text('blocks')
            for t in tabs.tables:
                x0, y0, x1, y1 = t.bbox
                # section header = last text block fully above table top, excluding running header/page num
                sec = ''
                best_y = -1
                for b in blocks:
                    bx0, by0, bx1, by1, txt, bn, bt = b
                    if bt != 0:
                        continue
                    if by1 <= y0 + 2 and by0 > 55 and by0 < 800:
                        clean = ' '.join(txt.split())
                        if not clean or 'دفترچه راهنماي' in clean:
                            continue
                        if by0 > best_y:
                            best_y = by0
                            sec = clean
                rows = []
                for r in t.extract():
                    rows.append([fix_rtl(c) for c in r])
                out.write(json.dumps({
                    'file': fname, 'page': pno, 'section': sec,
                    'bbox': [round(v, 1) for v in t.bbox], 'rows': rows,
                }, ensure_ascii=False) + '\n')
        doc.close()
        print('done', fname, file=sys.stderr)
    out.close()

if __name__ == '__main__':
    main(sys.argv[2:], sys.argv[1])
