
import math
from SiEPIC.utils import get_technology, get_technology_by_name
from pya import *
import pya
import numpy as np

class zep_heater_wg(pya.PCellDeclarationHelper):
  """
  The PCell declaration for the heater straight waveguide.
  
  Authors: Jaspreet Jhoja, Lukas Chrostowski
  Modified by Sheri Jahan Chowdhury

  """

  def __init__(self):

    # Important: initialize the super class
    super(zep_heater_wg, self).__init__()
    TECHNOLOGY = get_technology_by_name('SiEPICfab_EBeam_ZEP')

    # declare the parameters
    self.param("w", self.TypeDouble, "Waveguide Width", default = 0.5)
    self.param("length", self.TypeDouble, "Waveguide length", default = 100)
    self.param("m_dw", self.TypeDouble, "Metal edge to Si Edge (um)", default = 3)
    self.param("m_w", self.TypeDouble, "Metal Width", default = 10)
    self.param("overlay", self.TypeDouble, "Overlay accuracy (optical litho) (um)", default = 1)
    self.param("overlay_ebl", self.TypeDouble, "Overlay accuracy (EBL) (um)", default = 0.05)
    self.param("silayer", self.TypeLayer, "Layer", default = TECHNOLOGY['Si_core'])
    self.param("layer_clad", self.TypeLayer, "Layer - Cladding", default = TECHNOLOGY['Si_clad'])
    self.param("mlayer", self.TypeLayer, "Metal Layer", default = TECHNOLOGY['M1'])
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'])
    self.param("clad_width", self.TypeDouble, "Cladding Width", default = 2)
    
    
    
    #self.param("textl", self.TypeLayer, "Text Layer", default = LayerInfo(10, 0))

    
  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "zep_heater_wg_%s-%.3f" % \
        (self.length, self.m_w)

  def coerce_parameters_impl(self):
    pass

  def can_create_from_shape(self, layout, shape, layer):
    return False
    
  def produce_impl(self):
      
    # This is the main part of the implementation: create the layout

    from math import pi, cos, sin
    from SiEPIC.utils import arc_wg, arc_wg_xy
    from SiEPIC._globals import PIN_LENGTH
    from SiEPIC.extend import to_itype

   # fetch the parameters
    dbu = self.layout.dbu
    ly = self.layout
    shapes = self.cell.shapes
    
    LayerSi = self.layer
    LayerSiN = ly.layer(self.silayer)
  #LayerSiSPN = ly.layer(LayerSiSP)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
    LayerM = ly.layer(self.mlayer)
    

    w = to_itype(self.w,dbu)
    length = to_itype(self.length,dbu)
    m_dw = to_itype(self.m_dw,dbu)
    m_w = to_itype(self.m_w,dbu)
    overlay = to_itype(self.overlay, dbu)
    overlay_ebl = to_itype(self.overlay_ebl, dbu)
    
    in_taper = 0; # length of taper
    taper_w = 0; # width of taper

    #draw the waveguide
    xtop = 0 - in_taper
    ytop = -1*(w/2)
    xbottom = length + in_taper
    ybottom = 1*(w/2)
    wg1 = Box(xtop, -w/2, xbottom, w/2)
    shapes(LayerSiN).insert(wg1)


    # Pins on the bottom waveguide side:    
    pin = Path([Point(xtop+PIN_LENGTH/2, 0), Point(xtop-PIN_LENGTH/2, 0)], w)
    shapes(LayerPinRecN).insert(pin)
    text = Text ("pin1", Trans(Trans.R0, xtop, 0))
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu      

    pin = Path([Point(xbottom-PIN_LENGTH/2, 0), Point(xbottom+PIN_LENGTH/2, 0)], w)
    shapes(LayerPinRecN).insert(pin)
    text = Text ("pin2", Trans(Trans.R0, xbottom, 0))
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu      

    
    #draw metal
    b = Box(0, m_dw+w/2, length, m_dw+w/2+m_w)
    shapes(LayerM).insert(b)
   # b = Box(0, -m_dw-w/2, length, -m_dw-w/2-m_w)
   # shapes(LayerMN).insert(b)


    
    t = Trans(Trans.R0, 0,0)
    text = Text ('Component=zep_heater_wg', t)
    shape = shapes(LayerDevRecN).insert(text)
    # shape.text_size = self.r*0.07/
    
    # Create the device recognition layer
    points = [pya.Point(0,0), pya.Point(length, 0)]
    path = pya.Path(points,(self.w+self.clad_width*2)/dbu)
    shapes(LayerDevRecN).insert(path.simple_polygon())
    
    # waveguide cladding
    points = [pya.Point(0,0), pya.Point(length, 0)]
    path = pya.Path(points,(self.w+self.clad_width*2)/dbu)
    shapes(ly.layer(self.layer_clad)).insert(path.simple_polygon())

    
    print('Done drawing the layout for - zep_heater_wg')
  