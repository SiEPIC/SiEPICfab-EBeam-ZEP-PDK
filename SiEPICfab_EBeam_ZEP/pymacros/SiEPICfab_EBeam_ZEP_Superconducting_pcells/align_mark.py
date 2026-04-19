# Waveguide Bragg grating
# imported from SiEPIC_EBeam_PDK.  Model does not exist. Layout only.

from . import *
import pya
from pya import *
import math


class align_mark(pya.PCellDeclarationHelper):

  def __init__(self):
    super(align_mark , self).__init__()

    from SiEPIC.utils import get_technology_by_name
    self.technology_name = 'SiEPICfab_EBeam_ZEP'
    TECHNOLOGY = get_technology_by_name(self.technology_name)
    self.TECHNOLOGY = TECHNOLOGY

    # Override NbTiN to hardcoded 1/69
    self.param("devrec", self.TypeLayer, "Layer -DevRec", default=TECHNOLOGY['DevRec'])
    self.param("marklayer", self.TypeLayer, "Au/Ti Layer", default=TECHNOLOGY['Ti/Au']) 
    # declare the parameters
    self.param("align_length", self.TypeDouble, "Alignment mark length (microns)", default = 10)
    self.param("align_width", self.TypeDouble, "Alignment mark width (microns)", default = 1)
    
  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "Alignment_mark _length-%.3f_width-%.3f" % (self.align_length, self.align_width)
  
  def can_create_from_shape_impl(self):
    return False


  def produce_impl(self):
    """
    coerce parameters (make consistent)
    """

    # fetch the parameters
    ly = self.layout    
    dbu = ly.dbu
    
    LayerMark = ly.layer(self.marklayer)
#    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
        
    L = self.align_length/dbu
    W = self.align_width/dbu
#    L2 = self.rect_length/dbu

    align_vertical = pya.Region()
    align_horizontal = pya.Region()
    rect_vertical = pya.Region()
    rect_horizontal = pya.Region()
    
    # central cross
    vertical_poly =pya.Polygon([pya.Point(-W/2,L/2), pya.Point(-W/2,-L/2), pya.Point(W/2,-L/2), pya.Point(W/2,L/2)])
    horizontal_poly = pya.Polygon([pya.Point(-L/2,W/2), pya.Point(-L/2,-W/2), pya.Point(L/2,-W/2), pya.Point(L/2,W/2)])
    align_vertical.insert(vertical_poly)
    align_horizontal.insert(horizontal_poly)
 

    Mark_region = align_vertical | align_horizontal
       
    Mark_region.insert((rect_vertical|rect_horizontal))
        
    self.cell.shapes(LayerMark).insert(Mark_region)
