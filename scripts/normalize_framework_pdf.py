"""Add Unicode mappings to PowerPoint's embedded CID fonts without redrawing.

PowerPoint exports the Toppan font as a subset of Adobe-Japan1. Supplying the
matching ToUnicode map makes the PDF portable to readers without Asian language
packs. Glyph outlines, positions, slide contents and images remain unchanged.
"""
import argparse
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.cffLib import CFFFontSet
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject

p=argparse.ArgumentParser()
p.add_argument('input',type=Path);p.add_argument('output',type=Path)
p.add_argument('--font',required=True,type=Path)
p.add_argument('--pptx',required=True,type=Path)
a=p.parse_args()
font=TTFont(a.font)
lookup={}
# Prefer the canonical Unicode code point when the font has compatibility aliases.
for code,name in sorted(font.getBestCmap().items(),reverse=True):
    if code<32:continue
    lookup[name]=code
# Resolve shared-glyph aliases using the actual characters in the supplied deck
# (e.g. its en dash, rather than the font's synonymous figure-dash mapping).
with ZipFile(a.pptx) as deck:
    chars=set()
    for name in deck.namelist():
        if name.startswith('ppt/slides/slide') and name.endswith('.xml'):
            tree=ET.fromstring(deck.read(name))
            for node in tree.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}t'):
                chars.update(node.text or '')
    for c in chars:
        if ord(c) in font.getBestCmap():lookup[font.getBestCmap()[ord(c)]]=ord(c)
reader=PdfReader(a.input)
writer=PdfWriter();writer.clone_document_from_reader(reader)
count=0
for page in writer.pages:
    for ref in page['/Resources'].get('/Font',{}).values():
        parent=ref.get_object()
        if '/ToUnicode' in parent:continue
        if 'ToppanBunkyu' not in str(parent.get('/BaseFont','')):continue
        child=parent['/DescendantFonts'][0].get_object()
        # Both supplied Toppan faces use the registered Adobe-Japan1 CID set.
        # The Unicode meaning of a CID is shared across these font families.
        info=child.get('/CIDSystemInfo',{})
        if str(info.get('/Registry'))!='Adobe' or str(info.get('/Ordering'))!='Japan1':
            raise ValueError('Unexpected CID character collection')
        stream=child['/FontDescriptor']['/FontFile3'].get_object()
        if stream['/Subtype']!='/CIDFontType0C':raise ValueError('Unexpected embedded font type')
        cff=CFFFontSet();cff.decompile(BytesIO(stream.get_data()),None)
        names=[n for n in cff.topDictIndex[0].charset if n!='.notdef']
        missing=[n for n in names if n not in lookup]
        if missing:raise ValueError(f'Unmapped glyphs: {missing}')
        mappings=[f'<{int(n[3:]):04X}> <{chr(lookup[n]).encode("utf-16-be").hex().upper()}>' for n in names]
        rows=['/CIDInit /ProcSet findresource begin','12 dict begin','begincmap',
              '/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def',
              '/CMapName /JAM-Toppan-UCS def','/CMapType 2 def',
              '1 begincodespacerange','<0000> <FFFF>','endcodespacerange']
        for start in range(0,len(mappings),100):
            chunk=mappings[start:start+100]
            rows += [f'{len(chunk)} beginbfchar',*chunk,'endbfchar']
        rows += ['endcmap','CMapName currentdict /CMap defineresource pop','end','end']
        cmap=DecodedStreamObject();cmap.set_data(('\n'.join(rows)+'\n').encode('ascii'))
        parent[NameObject('/ToUnicode')]=writer._add_object(cmap)
        count+=1
writer.write(a.output)
result=PdfReader(a.output)
assert len(result.pages)==len(reader.pages)
for x,y in zip(reader.pages,result.pages):
    assert x.get_contents().get_data()==y.get_contents().get_data(), 'Slide drawing content changed'
assert 'Coupledtransformerlayers' in ''.join(result.pages[0].extract_text().split())
print(f'Added {count} Unicode maps; drawing streams unchanged.')
