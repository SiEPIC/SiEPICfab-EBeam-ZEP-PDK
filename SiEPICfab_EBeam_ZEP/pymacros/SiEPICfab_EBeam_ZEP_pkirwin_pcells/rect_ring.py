import math
import pya
from pya import *


class rect_ring(pya.PCellDeclarationHelper):
  def __init__(self):

    super(rect_ring, self).__init__()
    from SiEPIC.utils import get_technology_by_name, load_Waveguides_by_Tech
    self.technology_name = 'SiEPICfab_EBeam_ZEP'
    TECHNOLOGY = get_technology_by_name(self.technology_name)
    self.TECHNOLOGY = TECHNOLOGY

    load_Waveguides_by_Tech(self.technology_name)

    # declare the parameters
    self.param("l", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
    self.param("clad", self.TypeLayer, "Cladding Layer", default = TECHNOLOGY['Si_clad'])
    self.param("l1",self.TypeDouble, "Length 1", default = 100)
    self.param("l2",self.TypeDouble, "Length 2", default = 100)
    self.param("w", self.TypeDouble,"Width",default = 0.5)
    self.param("gl",self.TypeDouble, "Gap Length",default = 10)
    self.param("g", self.TypeDouble,"Gap",default = 0.2)   
    self.param("p",self.TypeLayer,"Pin Layer",default = pya.LayerInfo(1,10))     
    self.param("devrec", self.TypeLayer, "Dev Rec Layer", default = TECHNOLOGY['DevRec'])

  def display_text_impl(self):
    return "Ring(L1=" + str(self.l1) + ",L2=" + ('%.3f' % self.l2) + ",G=" + ('%.3f' % self.g) + ",GapL="+('%.3f' % self.gl) + ")"
  
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
    l1 = self.l1/dbu
    l2 = self.l2/dbu
    w = self.w/dbu
    g = self.g/dbu
    gl = self.gl/dbu
    rad = 20/dbu

    ## Make straight sections
    # left
    box1 = pya.Region()
    xa = -w/2
    xb = w/2
    ya = rad
    yb = rad + l1
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(self.l_layer).insert(box1)
    # right
    box1 = pya.Region()
    xa = -w/2 + 2*rad + l2
    xb = w/2 + 2*rad + l2
    ya = rad
    yb = rad + l1
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(self.l_layer).insert(box1)
    # bottom
    box1 = pya.Region()
    xa = rad
    xb = rad + l2
    ya = -w/2
    yb = w/2
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(self.l_layer).insert(box1)
    # top
    box1 = pya.Region()
    xa = rad
    xb = rad + l2
    ya = -w/2 + 2*rad + l1
    yb = w/2 + 2*rad + l1
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(self.l_layer).insert(box1)

    ## Make straight sections cladding
    # left
    box1 = pya.Region()
    xa = -w/2 - 2/dbu
    xb = w/2 + 2/dbu
    ya = rad
    yb = rad + l1
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(LayerCladN).insert(box1)
    # right
    box1 = pya.Region()
    xa = -w/2 + 2*rad + l2 -2/dbu
    xb = w/2 + 2*rad + l2 + 2/dbu
    ya = rad
    yb = rad + l1
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(LayerCladN).insert(box1)
    # bottom
    box1 = pya.Region()
    xa = rad
    xb = rad + l2
    ya = -w/2 - 2/dbu
    yb = w/2 + 2/dbu
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(LayerCladN).insert(box1)
    # top
    box1 = pya.Region()
    xa = rad
    xb = rad + l2
    ya = -w/2 + 2*rad + l1 -2/dbu
    yb = w/2 + 2*rad + l1 + 2/dbu
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(LayerCladN).insert(box1)

    # Make curved sections by calling on my personal import
    cell_bentsection = ly.create_cell("waveguide_bend_bezier02_w05_r20","Personal Import")
    # bottom left
    t = Trans(Trans.R270,0,0)
    self.cell.insert(CellInstArray(cell_bentsection.cell_index(),t))
    # bottom right
    t = Trans(Trans.R0,l2+2*rad,0)
    self.cell.insert(CellInstArray(cell_bentsection.cell_index(),t))
    # top left
    t = Trans(Trans.R180,0,l1+2*rad)
    self.cell.insert(CellInstArray(cell_bentsection.cell_index(),t))
    # top right
    t = Trans(Trans.R90,l2+2*rad,l1+2*rad)
    self.cell.insert(CellInstArray(cell_bentsection.cell_index(),t))
    
    ## Make coupling region
    # top bend
    t = Trans(Trans.R90,0-w/2-g-w/2,l1+rad)
    self.cell.insert(CellInstArray(cell_bentsection.cell_index(),t))
    # straight section
    box1 = pya.Region()
    ya = l1
    yb = l1 - gl
    xa = -w/2 - g
    xb = -w/2 - g - w
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(self.l_layer).insert(box1)
    # bottom bend
    t = Trans(Trans.R0,0-w/2-g-w/2,l1-rad-gl)
    self.cell.insert(CellInstArray(cell_bentsection.cell_index(),t))

    # make pins
    #add the top bus pin
    p1 = [Point(0-rad-g-w+0.05/dbu,l1+rad),Point(0-rad-g-w-0.05/dbu,l1+rad)]
    p1c = Point(0-rad-g-w,l1+rad)
    pin=Path(p1,w)
    t = Trans(Trans.R0,0-rad-g-w,l1+rad)
    self.cell.shapes(self.p_layer).insert(pin)
    text=Text("pin1",t)
    self.cell.shapes(self.p_layer).insert(text)
    
    #add the bottom bus pin
    p1 = [Point(0-rad-g-w+0.05/dbu,l1-rad-gl),Point(0-rad-g-w-0.05/dbu,l1-rad-gl)]
    p1c = Point(0-rad-g-w,l1-rad-gl)
    pin=Path(p1,w)
    t = Trans(Trans.R0,0-rad-g-w,l1-rad-gl)
    self.cell.shapes(self.p_layer).insert(pin)
    text=Text("pin2",t)
    self.cell.shapes(self.p_layer).insert(text)

    # add devrec box
    box1 = pya.Region()
    xa = 0-rad-g-w
    xb = 2*rad + l2 + w/2
    ya = 0-w/2
    yb = 2*rad+l1+w/2
    box1.insert(pya.Box(xa,ya,xb,yb))
    self.cell.shapes(ly.layer(self.devrec)).insert(box1)
