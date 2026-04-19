# Waveguide Bragg grating
# imported from SiEPIC_EBeam_PDK.  Model does not exist. Layout only.

from . import *
import pya
from pya import *

class ebeam_pcell_nanowirestraight(pya.PCellDeclarationHelper):
  def __init__(self):
    super(ebeam_pcell_nanowirestraight, self).__init__()

    from SiEPIC.utils import get_technology_by_name
    self.technology_name = 'SiEPICfab_EBeam_ZEP'
    TECHNOLOGY = get_technology_by_name(self.technology_name)
    self.TECHNOLOGY = TECHNOLOGY

    # Override NbTiN to hardcoded 1/69
    self.param("layer", self.TypeLayer, "Layer - NW", default=TECHNOLOGY['NbTiN'])
    self.param("LayerMetal", self.TypeLayer, "Au/Ti Layer", default=TECHNOLOGY['Ti/Au'])    
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default=TECHNOLOGY['PinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default=TECHNOLOGY['DevRec'])

    self.param("nw_width", self.TypeDouble, "NW width (microns)", default=0.05)
    self.param("l", self.TypeDouble, "NW length (microns)", default=10.0)
  def coerce_parameters_impl(self):
    pass
    
  def display_text_impl(self):
    return "NbTiN nanowire straight(w" + ('%.3f' % int(self.nw_width)) + "_l" + ('%.3f' % int(self.l)) + ")"
    
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
    nw_width = self.nw_width/dbu
    l = self.l/dbu
    shapes = self.cell.shapes
    
    ###Fractal NW

    

    square1 = pya.Region()  
    #W = radius + 0.0005/dbu+w/2

    square1.insert(pya.Box(-l/2 , -nw_width/2, +l/2, +nw_width/2 )) #pya.Point(w/2+0.35,l/2), pya.Point(w/2+0.35,-l/2), pya.Point(0.35-w/2,l/2-s), pya.Point(w/2,l/2-s), pya.Point(w/2,-l/2)])
    #self.cell.shapes(LayerSiN).insert(square1)

    taper1 = pya.Region()
    taper1.insert(pya.Polygon([Point(-l/2, nw_width/2), Point(-l/2, -nw_width/2), Point(-(l/2 + 10/dbu), nw_width/2 + 2/dbu), Point(-(l/2 + 10/dbu), -nw_width/2 + 7/dbu)]))

    taper2 = pya.Region()
    taper1.insert(pya.Polygon([Point(l/2, nw_width/2), Point(l/2, -nw_width/2), Point(l/2 + 10/dbu, nw_width/2 + 2/dbu), Point(l/2 + 10/dbu, -nw_width/2 + 7/dbu)]))

    full_shape = square1 + taper1 + taper2
    
    taper1_extra = pya.Region()
    taper1_extra.insert(pya.Polygon([Point(-l/2, nw_width/2 + 0.02/dbu), Point(-l/2, -nw_width/2 - 0.02/dbu), Point(-(l/2 + 10/dbu), nw_width/2 + 2/dbu), Point(-(l/2 + 10/dbu), -nw_width/2 + 7/dbu)]))

    taper2_extra = pya.Region()
    taper2_extra.insert(pya.Polygon([Point(l/2, nw_width/2 + 0.02/dbu), Point(l/2, -nw_width/2 - 0.02/dbu), Point(l/2 + 10/dbu, nw_width/2 + 2/dbu), Point(l/2 + 10/dbu, -nw_width/2 + 7/dbu)]))

    
    overlap = taper1_extra + taper2_extra
    self.cell.shapes(LayerSiN).insert(full_shape)
    self.cell.shapes(LayerMetal).insert(overlap)
    w = l/2
    radius = l/2

    #draw devrec box
    devrec_box = [Point(l/2 + 10/dbu, -nw_width/2 - 0.02/dbu),Point(-(l/2 + 10/dbu), -nw_width/2 - 0.02/dbu), Point(-(l/2 + 10/dbu), -nw_width/2 + 7/dbu), Point(l/2 + 10/dbu, -nw_width/2 + 7/dbu)]
    #place devrec box	
    shapes(LayerDevRecN).insert(Polygon(devrec_box))
    
    t = Trans(Trans.R270, radius, l/4)
    text = Text ('NbTiNnanowire:w=%.3fu l=%.3fu'%(int(self.nw_width)*1000,int(self.l)*1000), t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = 0.5/dbu
      
      
############################################################## 