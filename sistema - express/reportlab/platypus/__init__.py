import re
from pathlib import Path

_TAGS = re.compile(r'<[^>]+>')

def _limpar(txt):
    txt = str(txt)
    txt = txt.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    txt = _TAGS.sub('', txt)
    return txt

class Paragraph:
    def __init__(self, text, style=None):
        self.text = _limpar(text)
        self.style = style
    def as_text(self):
        return self.text

class Spacer:
    def __init__(self, w, h):
        self.w=w; self.h=h
    def as_text(self):
        return ''

class PageBreak:
    def as_text(self):
        return '\f'

class KeepTogether(list):
    pass

class Image:
    def __init__(self, filename, width=None, height=None):
        self.filename=filename; self.width=width; self.height=height; self.hAlign='CENTER'
    def as_text(self):
        return ''

class TableStyle:
    def __init__(self, commands=None):
        self.commands = commands or []

class Table:
    def __init__(self, data, colWidths=None, repeatRows=0, **kwargs):
        self.data=data or []
        self.colWidths=colWidths
        self.repeatRows=repeatRows
        self.style=None
    def setStyle(self, style):
        self.style=style
    def as_text(self):
        lines=[]
        for row in self.data:
            vals=[]
            for cell in row:
                if hasattr(cell, 'as_text'):
                    vals.append(cell.as_text())
                else:
                    vals.append(_limpar(cell))
            lines.append(' | '.join(vals))
        return '\n'.join(lines)

class SimpleDocTemplate:
    def __init__(self, filename, pagesize=None, **kwargs):
        self.filename=filename
        self.pagesize=pagesize or (595,842)
        self.page=1
    def build(self, story, onFirstPage=None, onLaterPages=None):
        linhas=[]
        def add(obj):
            if obj is None:
                return
            if isinstance(obj, (list, tuple, KeepTogether)):
                for x in obj:
                    add(x)
                return
            if hasattr(obj, 'as_text'):
                txt=obj.as_text()
            else:
                txt=str(obj)
            if txt == '\f':
                linhas.append('\f')
            else:
                for line in str(txt).splitlines():
                    linhas.append(line)
                if isinstance(obj, Spacer):
                    linhas.append('')
        for item in story:
            add(item)
        _criar_pdf_texto(self.filename, linhas)

def _esc_pdf(s):
    s = str(s).encode('latin-1', 'replace').decode('latin-1')
    return s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

def _quebrar_linha(s, n=110):
    s=str(s)
    while len(s) > n:
        corte=s.rfind(' ',0,n)
        if corte < 20: corte=n
        yield s[:corte]
        s=s[corte:].lstrip()
    yield s

def _criar_pdf_texto(path, linhas):
    path=Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pages=[]; atual=[]
    for linha in linhas:
        if linha == '\f':
            pages.append(atual); atual=[]; continue
        for l in _quebrar_linha(linha):
            atual.append(l)
            if len(atual) >= 48:
                pages.append(atual); atual=[]
    if atual or not pages: pages.append(atual)
    objects=[]
    def obj(data):
        objects.append(data); return len(objects)
    catalog = obj('')
    pages_id = obj('')
    page_ids=[]
    font_id = obj('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
    for page in pages:
        content=['BT','/F1 8 Tf','40 800 Td','12 TL']
        for line in page:
            content.append(f'({_esc_pdf(line)}) Tj')
            content.append('T*')
        content.append('ET')
        stream='\n'.join(content).encode('latin-1','replace')
        cont_id=obj(f'<< /Length {len(stream)} >>\nstream\n'+stream.decode('latin-1')+'\nendstream')
        page_id=obj(f'<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 842 595] /Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {cont_id} 0 R >>')
        page_ids.append(page_id)
    objects[catalog-1]=f'<< /Type /Catalog /Pages {pages_id} 0 R >>'
    kids=' '.join(f'{pid} 0 R' for pid in page_ids)
    objects[pages_id-1]=f'<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>'
    pdf=bytearray(b'%PDF-1.4\n')
    offsets=[0]
    for i,data in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f'{i} 0 obj\n'.encode('ascii'))
        pdf.extend(data.encode('latin-1','replace'))
        pdf.extend(b'\nendobj\n')
    xref=len(pdf)
    pdf.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode('ascii'))
    for off in offsets[1:]:
        pdf.extend(f'{off:010d} 00000 n \n'.encode('ascii'))
    pdf.extend(f'trailer\n<< /Size {len(objects)+1} /Root {catalog} 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode('ascii'))
    path.write_bytes(pdf)
