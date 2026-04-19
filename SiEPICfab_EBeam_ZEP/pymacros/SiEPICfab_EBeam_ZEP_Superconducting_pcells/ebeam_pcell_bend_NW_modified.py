# Waveguide Bragg grating
# imported from SiEPIC_EBeam_PDK.  Model does not exist. Layout only.

from . import *
import pya
from pya import *
import math
class ebeam_pcell_bend_NW_modified(pya.PCellDeclarationHelper):
  def __init__(self):
    super(ebeam_pcell_bend_NW_modified, self).__init__()

    from SiEPIC.utils import get_technology_by_name
    self.technology_name = 'SiEPICfab_EBeam_ZEP'
    TECHNOLOGY = get_technology_by_name(self.technology_name)
    self.TECHNOLOGY = TECHNOLOGY

    # Override NbTiN to hardcoded 1/69
    self.param("layer", self.TypeLayer, "Layer - NW", default=TECHNOLOGY['NbTiN'])
    self.param("LayerMetal", self.TypeLayer, "Au/Ti Layer", default=TECHNOLOGY['Ti/Au'])
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default=TECHNOLOGY['PinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default=TECHNOLOGY['DevRec'])
    self.param("w", self.TypeDouble, "NW width (microns)", default = 0.05)
    self.param("l", self.TypeDouble, "NW length (microns)", default = 100)
    self.param("bend_w", self.TypeDouble, "Bend Width (microns)", default = 0.05)
    self.param("radius", self.TypeDouble, "radius (microns)", default = 0.1625)
    self.param("n_vertices", self.TypeInt, "Vertices of a hole", default = 128)


  def coerce_parameters_impl(self):
    pass
    
  def display_text_impl(self):
    return "NbTiNnanowire(w" + ('%.3f' % int(self.w)) +"_r"+('%.3f' % int(self.radius))+ "_l" + ('%.3f' % int(self.l)) + ")"
    
  def can_create_from_shape(self, layout, shape, layer):
    return False
    
  def produce_impl(self):
  
    # fetch the parameters
    dbu = self.layout.dbu
    ly = self.layout
    from math import pi, cos, sin, log, sqrt, acos

    LayerSi = self.layer
    LayerSiN = ly.layer(LayerSi)
    LayerSi = self.layer
    LayerSiN = ly.layer(LayerSi)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
    LayerMetal = self.LayerMetal #Ti/Au layer
    LayerMetal = ly.layer(LayerMetal)

    w = self.w/dbu
    l = self.l/dbu
    radius = self.radius/dbu
    bend_w = self.bend_w/dbu
    n_vertices = self.n_vertices
    shapes = self.cell.shapes
    
    # function to generate points to create a circle
    def circle(x,y,r):
      npts = 2*n_vertices
      theta = 2*math.pi / npts # increment, in radians
      pts = []
      for i in range(0, npts+1):
        pts.append(Point.from_dpoint(pya.DPoint((x+r*math.cos(i*theta))/1, (y+r*math.sin(i*theta))/1)))
      return pts
    # function to generate points to create a circle
    def halfcircle(x,y,r):
      npts = n_vertices
      theta = math.pi / npts # increment, in radians
      pts = []
      for i in range(0, npts+1):
        pts.append(Point.from_dpoint(pya.DPoint((x+r*math.cos(i*theta))/1, (y+r*math.sin(i*theta))/1)))
      return pts

    curve1 = pya.Region()  
    R = radius+w
    Y = l/2-0.001/dbu
    halfCircle_cell = halfcircle(0,Y,R)
    halfCircle_poly = pya.Polygon(halfCircle_cell)
    curve1.insert(halfCircle_poly)   


    curve2 = pya.Region()  
    R = radius
    Y = l/2 - 0.001/dbu
    halfCircle_cell = halfcircle(0,Y,R)
    halfCircle_poly = pya.Polygon(halfCircle_cell)
    curve2.insert(halfCircle_poly)   
    #self.cell.shapes(LayerSiN).insert(curve) 
         
    square1 = pya.Region()  
    #W = radius + 0.0005/dbu+w/2
    W = radius + w
    square1.insert(pya.Box(-W, -l/2, W, l/2)) #pya.Point(w/2+0.35,l/2), pya.Point(w/2+0.35,-l/2), pya.Point(0.35-w/2,l/2-s), pya.Point(w/2,l/2-s), pya.Point(w/2,-l/2)])
    #self.cell.shapes(LayerSiN).insert(square1)

    square2 = pya.Region()
    #W_2 = radius+ 0.0005/dbu-w/2
    W_2 = radius
    square2.insert(pya.Box(-W_2, -l/2, W_2, Y + 0.001/dbu))
    #self.cell.shapes(LayerSiN).insert(square2)

    taper1 = pya.Region()
    taper1.insert(pya.Polygon([Point(-W, -l/2), Point(-W+w,-l/2), Point(-W+w-2/dbu,-l/2-10/dbu), Point(-W-7/dbu,-l/2-10/dbu)]))
    
    taper2 = pya.Region()
    taper1.insert(pya.Polygon([Point(W, -l/2), Point(W-w,-l/2), Point(W-w+2/dbu,-l/2-10/dbu), Point(W+7/dbu,-l/2-10/dbu)]))
    
    full_shape = square1 - square2 + curve1 - curve2 + taper1 + taper2
    taper1_extra = pya.Region()
    taper1_extra.insert(pya.Polygon([Point(-W - 0.02/dbu, -l/2), Point(-W+w + 0.02/dbu,-l/2), Point(-W+w-2/dbu,-l/2-10/dbu), Point(-W-7/dbu,-l/2-10/dbu)]))
    
    taper2_extra = pya.Region()
    taper2_extra.insert(pya.Polygon([Point(W+ 0.02/dbu, -l/2), Point(W-w - 0.02/dbu,-l/2), Point(W-w+2/dbu,-l/2-10/dbu), Point(W+7/dbu,-l/2-10/dbu)]))
    
    overlap = taper1_extra + taper2_extra
    
    
    self.cell.shapes(LayerSiN).insert(full_shape)
    self.cell.shapes(LayerMetal).insert(overlap)


    # Pins on the nanowire end:
    pin = Path([Point(-W+w/2-4.5/dbu,-l/2-10/dbu+w), Point(-W+w/2-4.5/dbu, -w-l/2-10/dbu)], w+5/dbu)
    shapes(LayerPinRecN).insert(pin)
    text = Text ("pin2", Trans(Trans.R270, -W+w/2-4.5/dbu, -l/2-10/dbu))
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    pin = Path([Point(W-w/2+4.5/dbu,-l/2-10/dbu+w),Point(W-w/2+4.5/dbu, -w-l/2-10/dbu)], w+5/dbu)
    shapes(LayerPinRecN).insert(pin)
    text = Text ("pin1", Trans(Trans.R270, W-w/2+4.5/dbu, -l/2-10/dbu))
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu
    
    #draw devrec box
    devrec_box = [Point(-2*(radius+2*w),-l/2),Point(2*(radius+2*w),-l/2),Point(2*(radius+2*w),l/2),Point(-2*(radius+2*w),l/2)]
    #place devrec box
    shapes(LayerDevRecN).insert(Polygon(devrec_box))
    
    t = Trans(Trans.R270, radius, l/4)
    text = Text ('NbTiNnanowire:w=%.3fu r=%.3fu l=%.3fu'%(int(self.w)*1000,int(self.radius)*1000,int(self.l)*1000), t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = 0.5/dbu