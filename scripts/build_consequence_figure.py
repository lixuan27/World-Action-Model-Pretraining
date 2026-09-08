"""Publication figure for consequence supervision; examples are schematic.

The image is reused unchanged from the user's reference deck. All labels,
coordinate geometry, masks, arrows and tokens remain editable vector objects.
"""
from pathlib import Path
import glob, hashlib, json, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle, FancyBboxPatch, PathPatch, Polygon
from matplotlib.path import Path as MplPath
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Figures'
ASSET=OUT/'assets/consequence_tracks_illustration.png'
FONT_PATH=os.environ.get('JAM_FIGURE_FONT')
if not FONT_PATH:
    fonts=glob.glob('/System/Library/AssetsV2/com_apple_MobileAsset_Font8/*/AssetData/ToppanBunkyuMinchoPr6N-Regular.otf')
    FONT_PATH=fonts[0] if fonts else None
if not FONT_PATH:
    raise RuntimeError('Set JAM_FIGURE_FONT to ToppanBunkyuMinchoPr6N-Regular.otf. Committed PDFs compile without regenerating.')
FONT=FontProperties(family='Toppan Bunkyu Mincho',fname=FONT_PATH)
# Type 3 embeds vector glyph outlines correctly for the supplied CFF/OpenType
# font; treating the CFF file as a TrueType CID font causes PDF font warnings.
plt.rcParams.update({'pdf.fonttype':3,'ps.fonttype':3,'mathtext.fontset':'stix','svg.hashsalt':'jam-consequence-v1'})
INK='#263A48'; LINE='#8496A4'; BLUE='#527B98'; TEAL='#587F78'
PALE_BLUE='#E5EEF4'; PALE_TEAL='#E5EFEC'; GREY='#899198'; PALE_GREY='#F1F4F5'; RED='#8C3340'
FONT.set_math_fontfamily('stix')
W,H=16,6.25
fig=plt.figure(figsize=(W,H),dpi=120,facecolor='white')
ax=fig.add_axes([0,0,1,1]); ax.set(xlim=(0,W),ylim=(H,0),aspect='equal'); ax.axis('off')
texts=[]
def text(x,y,s,size=20,color=INK,ha='center',va='center',**kw):
    t=ax.text(x,y,s,fontproperties=FONT,fontsize=size,color=color,ha=ha,va=va,**kw)
    texts.append(t); return t

def box(x,y,w,h,fill='white',edge=LINE,lw=.8,radius=.035):
    p=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={radius}',facecolor=fill,edgecolor=edge,linewidth=lw)
    ax.add_patch(p); return p

def line(points,color=GREY,lw=1.,**kwargs):
    p=np.array(points); ax.plot(p[:,0],p[:,1],color=color,lw=lw,**kwargs)

def arrow(start,end,color=GREY,width=.035,head=.105,headwidth=.13):
    a,b=np.array(start),np.array(end); u=(b-a)/np.linalg.norm(b-a); n=np.array([-u[1],u[0]])
    neck=b-head*u
    v=[a+width/2*n,neck+width/2*n,neck+headwidth/2*n,b,neck-headwidth/2*n,neck-width/2*n,a-width/2*n]
    ax.add_patch(Polygon(v,closed=True,facecolor=color,edgecolor=color,linewidth=.45))

def dot(x,y,color,open_=False,r=.06):
    ax.add_patch(Circle((x,y),r,facecolor='white' if open_ else color,edgecolor=color,linewidth=1.35))

# Flat composition with one continuous left-to-right flow.
for x,title in [(2.65,'(a) Tracked interaction'),(7.55,'(b) Anchor-relative target'),(13.20,'(c) Masked joint training')]:
    text(x,.30,title,23.5)
for x0,x1 in [(.12,5.22),(5.90,9.98),(10.62,15.90)]:
    line([(x0,.64),(x1,.64)],'#C8D4DB',.75)

# A. Unchanged reference illustration; its plane represents image coordinates.
ax.imshow(plt.imread(ASSET),extent=(.05,5.35,4.33,.80),zorder=0)
text(1.23,4.23,'Current anchors',20)
text(4.23,1.00,'Future points',20,TEAL)
for x,label,col,opened in [(.35,'Anchor',INK,False),(2.08,'Visible',TEAL,False),(3.78,'Occluded',TEAL,True)]:
    dot(x,4.65,col,opened,.065); text(x+.16,4.65,label,20,ha='left')
line([(.33,5.02),(5.05,5.02)],'#D5DDE2',.7)
text(2.67,5.37,'Robot: actuator / scene tracks',20)
text(2.67,5.86,'Human: projected hand poses',20)

# B. Curved track vs. straight anchor-to-future displacement.
arrow((5.27,2.87),(5.82,2.87),RED,.10,.18,.29)
box(6.13,1.02,3.60,3.03,PALE_GREY,'#C9D5DC',.65)
for x in np.linspace(6.13,9.73,5)[1:-1]: line([(x,1.02),(x,4.05)],'#DEE5E9',.5)
for y in np.linspace(1.02,4.05,5)[1:-1]: line([(6.13,y),(9.73,y)],'#DEE5E9',.5)
text(7.93,.85,'Image coordinates',20,GREY)
q0=(6.62,3.46); qt=(9.28,1.48); elbow=(qt[0],q0[1])
path=MplPath([q0,(7.90,3.75),(7.65,1.27),qt],[MplPath.MOVETO,MplPath.CURVE4,MplPath.CURVE4,MplPath.CURVE4])
ax.add_patch(PathPatch(path,fill=False,edgecolor=BLUE,linewidth=1.5))
text(7.22,2.33,'track',20,BLUE)
arrow(q0,qt,TEAL,.025,.14,.12)
arrow(q0,elbow,GREY,.019,.12,.10); arrow(elbow,qt,GREY,.019,.12,.10)
line([(9.12,3.46),(9.12,3.30),(9.28,3.30)],GREY,.75)
dot(*q0,INK,r=.07); dot(*qt,TEAL,r=.07)
text(q0[0]-.18,q0[1]+.30,r'$q_{0,k}$',24)
text(qt[0]-.01,qt[1]-.29,r'$q_{t,k}$',24,TEAL)
text(7.98,3.74,r'$\Delta x$',23); text(9.50,2.50,r'$\Delta y$',23,rotation=90)
text(7.97,4.43,r'$d=g(q_{t,k}-q_{0,k})$',24)
for x,label,fill in [(6.23,r'$d_x$',PALE_BLUE),(7.41,r'$d_y$',PALE_BLUE),(8.59,r'$2b-1$',PALE_TEAL)]:
    box(x,4.88,1.06,.58,fill,LINE,.8); text(x+.53,5.16,label,23)
text(7.35,5.79,'Displacement',20,BLUE); text(9.11,5.79,'Visibility',20,TEAL)

# C. Binary visibility examples. Masked target zeros are storage values.
arrow((10.04,2.87),(10.58,2.87),RED,.10,.18,.29)
text(12.90,.97,r'Target $c$',21); text(14.96,.97,r'Mask $M$',21)
cx=[12.30,12.90,13.50,14.38,14.98,15.58]
for x,label in zip(cx,['x','y','vis.','x','y','vis.']): text(x,1.45,label,20)
for y,label,values,mask in [(2.03,'Visible',[r'$d_x$',r'$d_y$','+1'],[1,1,1]),(2.73,'Occluded',['0','0',r'$-1$'],[0,0,1]),(3.43,'Missing',['0','0','0'],[0,0,0])]:
    text(10.67,y,label,20,ha='left')
    for j,x in enumerate(cx):
        k=j%3; valid=mask[k]
        fill=(PALE_TEAL if k==2 else PALE_BLUE) if valid else PALE_GREY
        box(x-.275,y-.25,.55,.5,fill,'#C7D2D9',.65)
        text(x,y,values[k] if j<3 else str(valid),22,(TEAL if k==2 else BLUE) if valid else '#A0A9AF')
line([(13.88,1.28),(13.88,3.74)],'#C2CED5',.8)
text(12.65,3.96,'Colored: supervised',20,GREY)
arrow((14.98,3.77),(14.98,4.47),GREY,.028,.11,.12)
text(15.30,4.13,r'$M$',21,GREY)

# Projection into consequence tokens and the existing joint flow objective.
arrow((12.49,4.16),(12.49,4.46),GREY,.033,.10,.13)
for dx,dy,fill in [(.16,-.16,'#E0E7EA'),(.08,-.08,'#EEF2F4'),(0,0,'#F8FAFB')]: box(11.16+dx,4.62+dy,2.37,.72,fill,LINE,.75)
for row in range(2):
    for col in range(6):
        valid=(row,col) not in [(0,4),(1,4),(1,5)]
        box(11.28+col*.355,4.74+row*.25,.27,.17,'#90B2AC' if valid else '#E8EDF0','#D4DDE2',.35,.009)
text(12.38,5.74,'Consequence tokens',20)
arrow((13.82,4.98),(14.33,4.98),RED,.08,.15,.23)
box(14.42,4.56,1.44,.91,PALE_BLUE,LINE,.8)
text(15.14,4.82,'JAM',24); text(15.14,5.20,r'$\mathcal{L}_c$',24,TEAL)
text(15.14,5.75,'Joint flow',20)

fig.canvas.draw(); renderer=fig.canvas.get_renderer()
bounds=[(t,t.get_window_extent(renderer)) for t in texts]
outside=[t.get_text() for t,b in bounds if b.x0<0 or b.y0<0 or b.x1>fig.bbox.width or b.y1>fig.bbox.height]
overlaps=[]
for i,(ta,a) in enumerate(bounds):
    for tb,b in bounds[i+1:]:
        if min(a.x1,b.x1)-max(a.x0,b.x0)>2 and min(a.y1,b.y1)-max(a.y0,b.y0)>2: overlaps.append([ta.get_text(),tb.get_text()])
if outside or overlaps: raise RuntimeError({'outside':outside,'text_overlaps':overlaps})
fig.savefig(OUT/'consequence_interface.pdf',metadata={'CreationDate':None})
fig.savefig(OUT/'consequence_interface.png',dpi=180)
plt.rcParams['svg.fonttype']='none'; fig.savefig(OUT/'consequence_interface.svg',metadata={'Date':None})
plt.rcParams['svg.fonttype']='path'; fig.savefig(OUT/'consequence_interface_outlined.svg',metadata={'Date':None})
plt.close(fig)
qa={'figure':'consequence_interface','font':FONT.get_name(),'math_font':'STIX serif','formats':['PDF','PNG','editable SVG','outlined SVG'],
    'text_bounds':'PASS','text_intersections':'PASS','smallest_text_pt_at_6_5_in':round(20*6.5/W,2),
    'source':'Sections/4_Pretraining.tex and consequence target assembly in the archived source audit',
    'mask_examples':{'visible':[1,1,1],'occluded':[0,0,1],'missing':[0,0,0]},
    'illustration':{'status':'Schematic, not an experimental observation or model prediction',
      'reference':'User-supplied JAM-framework-joint-flow-v9.pptx, slide 1, ppt/media/image36.png',
      'sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),'modification':'Unchanged image placement'},
    'reference_thread':'01a07e80-5bdf-71f3-b277-99058429ac35'}
(ROOT/'artifacts/consequence_figure_qa.json').write_text(json.dumps(qa,indent=2)+'\n')
print('Built consequence interface: PDF, PNG and editable/outlined SVGs.')
