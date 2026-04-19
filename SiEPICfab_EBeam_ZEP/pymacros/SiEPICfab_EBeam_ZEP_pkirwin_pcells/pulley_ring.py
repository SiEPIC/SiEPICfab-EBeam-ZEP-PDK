import math
import pya
from pya import *

class pulley_ring(pya.PCellDeclarationHelper):
  """
  author: Phillip Kirwin - pkirwin@ece.ubc.ca 
  """
  def __init__(self):

    super(pulley_ring, self).__init__()
    from SiEPIC.utils import get_technology_by_name, load_Waveguides_by_Tech
    self.technology_name = 'SiEPICfab_EBeam_ZEP'
    TECHNOLOGY = get_technology_by_name(self.technology_name)
    self.TECHNOLOGY = TECHNOLOGY

    load_Waveguides_by_Tech(self.technology_name)

    # declare the parameters
    self.param("l", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
    self.param("clad", self.TypeLayer, "Cladding Layer", default = TECHNOLOGY['Si_clad'])
    self.param("r", self.TypeDouble, "Radius", default = 300)
    self.param("w", self.TypeDouble,"Width",default = 3)
    self.param("w2", self.TypeDouble,"Bus Width",default = 3)
    self.param("g", self.TypeDouble,"Gap",default = 0.2)
    self.param("n", self.TypeInt, "Number of points", default = 2048)     
    self.param("p",self.TypeLayer,"Pin Layer",default = pya.LayerInfo(1,10))     
    self.param("devrec", self.TypeLayer, "Dev Rec Layer", default = TECHNOLOGY['DevRec'])

  def display_text_impl(self):
    return "Ring(L=" + str(self.l) + ",R=" + ('%.3f' % self.r) + ",G=" + ('%.3f' % self.g) + ",BusW="+('%.3f' % self.w2) + ")"
  
  def coerce_parameters_impl(self):
    pass

  def can_create_from_shape(self, layout, shape, layer):
    return False
  
  def produce_impl(self):
     
    # compute the arc
    # fetch the parameters
    from SiEPIC._globals import PIN_LENGTH
    from SiEPIC.extend import to_itype
    import math
    from pya import DPolygon
    
    pi  = math.pi
    # This is the main part of the implementation: create the layout


    dbu = self.layout.dbu
    ly = self.layout
    shapes = self.cell.shapes
    LayerCladN = ly.layer(self.clad)
    pts_o = []
    pts_i = []
    da = 2*pi / (self.n)
    r = self.r/dbu
    r2 = self.r
    w = self.w/dbu
    w2 = self.w2/dbu
    g = self.g/dbu
      
    #create the circle
    for i in range(0,self.n+1):
      bend_ox = (r+w/2)*math.cos(i*da)
      bend_oy = (r+w/2)*math.sin(i*da)
      bend_ix = (r-w/2)*math.cos(i*da)
      bend_iy = (r-w/2)*math.sin(i*da)
      pts_o.append(pya.Point.from_dpoint(pya.DPoint(bend_ox,bend_oy)))
      pts_i.append(pya.Point.from_dpoint(pya.DPoint(bend_ix,bend_iy)))
    
    pts_o.append(pya.Point.from_dpoint(pya.DPoint(0,r+w/2)))
    pts_i.append(pya.Point.from_dpoint(pya.DPoint(0,r-w/2)))
    pts_o.append(pya.Point.from_dpoint(pya.DPoint(0,0)))
    pts_i.append(pya.Point.from_dpoint(pya.DPoint(0,0)))
    ring1=pya.Region()
    ring1.insert(pya.Polygon(pts_o))
    ring2=pya.Region()
    ring2.insert(pya.Polygon(pts_i))
    ring = ring1-ring2
    self.cell.shapes(self.l_layer).insert(ring)

    #Add cladding for inversion around the ring
    pts_o = []
    pts_i = []
    for i in range(0,self.n+1):
      bend_ox = (r+w/2+2/dbu)*math.cos(i*da)
      bend_oy = (r+w/2+2/dbu)*math.sin(i*da)
      bend_ix = (r-w/2-2/dbu)*math.cos(i*da)
      bend_iy = (r-w/2-2/dbu)*math.sin(i*da)
      pts_o.append(pya.Point.from_dpoint(pya.DPoint(bend_ox,bend_oy)))
      pts_i.append(pya.Point.from_dpoint(pya.DPoint(bend_ix,bend_iy)))
    
    pts_o.append(pya.Point.from_dpoint(pya.DPoint(0,r+w/2+2/dbu)))
    pts_i.append(pya.Point.from_dpoint(pya.DPoint(0,r-w/2-2/dbu)))
    pts_o.append(pya.Point.from_dpoint(pya.DPoint(0,0)))
    pts_i.append(pya.Point.from_dpoint(pya.DPoint(0,0)))
    ring1=pya.Region()
    ring1.insert(pya.Polygon(pts_o))
    ring2=pya.Region()
    ring2.insert(pya.Polygon(pts_i))
    ring = ring1-ring2
    self.cell.shapes(LayerCladN).insert(ring)
    
    #DEV BOX
    self.cell.shapes(ly.layer(self.devrec)).insert(Box(DPoint(-to_itype(r2+5,dbu),-to_itype(r2+w/2*dbu,dbu)),DPoint(to_itype(r2+5,dbu),to_itype(r2+5,dbu))))

    #insert curved bus waveguide
    pts_o = []
    pts_i = []
    for i in range(0,int(self.n/2)+1):
      bend_ox = (r+w/2+g+w2)*math.cos(i*da)
      bend_oy = (r+w/2+g+w2)*math.sin(i*da)
      bend_ix = (r+w/2+g)*math.cos(i*da)
      bend_iy = (r+w/2+g)*math.sin(i*da)
      pts_o.append(pya.Point.from_dpoint(pya.DPoint(bend_ox,bend_oy)))
      pts_i.append(pya.Point.from_dpoint(pya.DPoint(bend_ix,bend_iy)))
    
    ring1=pya.Region()
    ring1.insert(pya.Polygon(pts_o))
    ring2=pya.Region()
    ring2.insert(pya.Polygon(pts_i))
    ring = ring1-ring2
    self.cell.shapes(self.l_layer).insert(ring)

    ## insert straight sections of bus waveguide
    # left
    box1 = pya.Region()
    xa = -(r+w/2+g+w2)
    xb = -(r+w/2+g)
    ya = 0
    yb = -r-w/2
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(self.l_layer).insert(box1)
    # right
    box1 = pya.Region()
    xa = r+w/2+g+w2
    xb = r+w/2+g
    ya = 0
    yb = -r-w/2
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(self.l_layer).insert(box1)

    ## adding bus waveguide cladding
    # curved part
    pts_o = []
    pts_i = []
    for i in range(0,int(self.n/2)+1):
      bend_ox = (r+w/2+g+w2+2/dbu)*math.cos(i*da)
      bend_oy = (r+w/2+g+w2+2/dbu)*math.sin(i*da)
      bend_ix = (r+w/2+g-2/dbu)*math.cos(i*da)
      bend_iy = (r+w/2+g-2/dbu)*math.sin(i*da)
      pts_o.append(pya.Point.from_dpoint(pya.DPoint(bend_ox,bend_oy)))
      pts_i.append(pya.Point.from_dpoint(pya.DPoint(bend_ix,bend_iy)))
    
    ring1=pya.Region()
    ring1.insert(pya.Polygon(pts_o))
    ring2=pya.Region()
    ring2.insert(pya.Polygon(pts_i))
    ring = ring1-ring2
    self.cell.shapes(LayerCladN).insert(ring)

    # straight parts
    # left
    box1 = pya.Region()
    xa = -(r+w/2+g+w2+2/dbu)
    xb = -(r+w/2+g-2/dbu)
    ya = 0
    yb = -r-w/2
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(LayerCladN).insert(box1)
    # right
    box1 = pya.Region()
    xa = r+w/2+g+w2+2/dbu
    xb = r+w/2+g-2/dbu
    ya = 0
    yb = -r-w/2
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(LayerCladN).insert(box1)

    
    #add the left bus pin
    yp1 = -0.05/self.layout.dbu
    yp2 = 0.05/self.layout.dbu
    xp1 = -(r+w/2+g+w2/2)
    p1 = [Point(xp1,yb+yp2),Point(xp1,yb+yp1)]
    p1c = Point(xp1,yb)
    self.set_p1=p1c
    self.p1=p1c
    pin=Path(p1,w2)
    t = Trans(Trans.R90,xp1,yb)
    self.cell.shapes(self.p_layer).insert(pin)
    text=Text("pin1",t)
    self.cell.shapes(self.p_layer).insert(text)
    
    #add the right bus pin
    xp1 = r+w/2+g+w2/2
    p2 = [Point(xp1,yb+yp2),Point(xp1,yb+yp1)]
    p2c = Point(xp1,yb)
    self.set_p2=p2c
    self.p2=p2c
    pin=Path(p2,w2)
    t = Trans(Trans.R90,xp1,yb)
    self.cell.shapes(self.p_layer).insert(pin)
    text=Text("pin2",t)
    self.cell.shapes(self.p_layer).insert(text)
