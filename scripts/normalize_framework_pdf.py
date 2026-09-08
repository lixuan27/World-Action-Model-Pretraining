"""Add Unicode mappings to PowerPoint's embedded CID fonts without redrawing.

PowerPoint exports the Toppan font as a subset of Adobe-Japan1. Supplying the
matching ToUnicode map makes the PDF portable to readers without Asian language
packs. Page selection and outer cropping preserve drawing content. An optional,
explicitly audited correction separates two overlapping labels in the supplied teaser.
"""
import argparse
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.cffLib import CFFFontSet
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject, RectangleObject

p=argparse.ArgumentParser()
p.add_argument('input',type=Path);p.add_argument('output',type=Path)
p.add_argument('--font',required=True,type=Path)
p.add_argument('--pptx',required=True,type=Path)
p.add_argument('--slide',type=int,help='One-based slide to export; default exports every slide.')
p.add_argument('--crop',nargs=4,type=float,metavar=('LEFT','BOTTOM','RIGHT','TOP'),
               help='PDF page bounds in points; trims outer whitespace without redrawing.')
p.add_argument('--teaser-spacing-fix',action='store_true',
               help='Move the supplied teaser Independent label left 8 pt to separate adjacent labels.')
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
writer=PdfWriter()
if a.slide is not None:
    if not 1<=a.slide<=len(reader.pages):raise ValueError('Slide is outside the input PDF')
    source_pages=[reader.pages[a.slide-1]]
    writer.add_page(source_pages[0])
else:
    source_pages=list(reader.pages)
    writer.clone_document_from_reader(reader)
count=0
spacing_before=b'0.24 0 0 0.24 307.4818 -384.24\ncm BT 0.0018 Tc'
spacing_after=b'0.24 0 0 0.24 299.4818 -384.24\ncm BT 0.0018 Tc'
if a.teaser_spacing_fix and len(writer.pages)!=1:
    raise ValueError('Spacing correction requires a single selected teaser page')
for page in writer.pages:
    if a.crop:
        left,bottom,right,top=a.crop
        if not (page.mediabox.left<=left<right<=page.mediabox.right and
                page.mediabox.bottom<=bottom<top<=page.mediabox.top):
            raise ValueError('Crop is outside the source page')
        page.mediabox=RectangleObject(a.crop)
        page.cropbox=RectangleObject(a.crop)
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
    if a.teaser_spacing_fix:
        data=page.get_contents().get_data()
        if data.count(spacing_before)!=1:raise ValueError('Expected teaser label position changed')
        corrected=DecodedStreamObject();corrected.set_data(data.replace(spacing_before,spacing_after))
        page[NameObject('/Contents')]=writer._add_object(corrected)
writer.write(a.output)
result=PdfReader(a.output)
assert len(result.pages)==len(source_pages)
for x,y in zip(source_pages,result.pages):
    expected=x.get_contents().get_data()
    if a.teaser_spacing_fix:expected=expected.replace(spacing_before,spacing_after)
    assert expected==y.get_contents().get_data(), 'Unexpected slide drawing change'
assert all(page.extract_text().strip() for page in result.pages), 'Text extraction is empty'
print(f'Added {count} Unicode maps; '+('only Independent label shifted left 8 pt.' if a.teaser_spacing_fix else 'drawing streams unchanged.'))
