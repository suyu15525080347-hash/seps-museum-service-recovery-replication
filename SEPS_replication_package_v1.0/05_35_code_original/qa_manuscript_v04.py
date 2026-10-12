# -*- coding: utf-8 -*-
import sys, os, re, json, subprocess, hashlib, docx
sys.stdout.reconfigure(encoding='utf-8')
OUT = r'D:\seps_fig_work\ms'
md = open(os.path.join(OUT, 'SEPS_full_manuscript_v0.4_figures_integrated.md'), encoding='utf-8').read()
D = docx.Document(os.path.join(OUT, 'SEPS_manuscript_v0.4_figures_integrated.docx'))
txt = '\n'.join(p.text for p in D.paragraphs)
abs_md = md.split('## Abstract')[1].split('**Keywords')[0].strip()
abs_dx = [p.text for p in D.paragraphs][2]
body = txt.split('Tables and figures')[0]
qa = {
 'abstract_words_md': len(abs_md.split()), 'abstract_words_docx': len(abs_dx.split()),
 'body_words_docx_before_references': len(txt.split('References')[0].split()),
 'stale_HMT_1.1493': txt.count('1.1493') + md.count('1.1493'), 'stale_HMT_1.0597': txt.count('1.0597') + md.count('1.0597'),
 'June_HMT_mentions': len(re.findall(r'June 2026 (GDP|deflator|HM Treasury)', txt)),
 'Figure0_in_body': body.count('Figure 0'),
 'callouts_in_body': {f'Figure {k}': body.count(f'Figure {k}') + body.count(f'Fig. {k}') for k in range(1, 6)},
 'supp_S1_callout': body.count('Supplementary Fig. S1'),
 'figure_images_in_docx': len(D.inline_shapes),
 'frozen_numbers_present': {k: (k in txt) for k in ['0.2299', '0.2200', '0.2407', '0.2447', '1.1502', '1.0605', '0.9801', '0.9623', '0.1223', '0.2168', '0.3737']},
}
# render
soffice = r'C:\Program Files\LibreOffice\program\soffice.exe'
pdfdir = os.path.join(OUT, 'render'); os.makedirs(pdfdir, exist_ok=True)
for f in ['SEPS_manuscript_v0.4_figures_integrated.docx', 'SEPS_supplementary_Fig_S1_workflow_v0.4.docx']:
    subprocess.run([soffice, '--headless', '--convert-to', 'pdf', '--outdir', pdfdir, os.path.join(OUT, f)], capture_output=True, timeout=300)
import fitz
pdf = fitz.open(os.path.join(pdfdir, 'SEPS_manuscript_v0.4_figures_integrated.pdf'))
qa['pdf_pages'] = pdf.page_count
blank = []
for i, pg in enumerate(pdf):
    t = pg.get_text().strip(); imgs = pg.get_images()
    if len(t) < 40 and not imgs: blank.append(i + 1)
    pix = pg.get_pixmap(dpi=60); pix.save(os.path.join(pdfdir, f'p{i + 1:02d}.png'))
qa['blank_pages'] = blank
qa['figure_pages'] = [i + 1 for i, pg in enumerate(pdf) if pg.get_images()]
json.dump(qa, open(os.path.join(OUT, 'SEPS_manuscript_v0.4_QA.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(json.dumps(qa, indent=1, ensure_ascii=False))
