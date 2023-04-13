"""
    Directional Coupler PCell for SiEPIC-TOOLS EPDA
    
    Author:     Mustafa Hammood
    Email:      Mustafa@siepic.com
    Affl:       SiEPIC Kits Ltd.
    Copyright 2023
"""

import pya
from pya import *
from SiEPIC.utils import get_technology_by_name

def make_pin(cell, name, center, w, pin_length, layer, vertical = 0):
  """Handy method to create a pin on a device to avoid repetitive code.

  Args:
      cell (pya cell): cell to create the pin on
      name (string): name of the pin
      center (list): center of the pin in dbu. Format: [x, y]
      w (int): width of the pin in dbu
      pin_length (int): length of the pin in dbu, change the sign to determine pin direction. Default is left-to-right.
      layer (pya layer): layer to create the pin on
      vertical (int, optional): flag to determine if pin is vertical or horizontal. Defaults to 0.
  """
  if vertical == 0:
    p1 = pya.Point(center[0]+pin_length/2, center[1])
    p2 = pya.Point(center[0]-pin_length/2, center[1])
  elif vertical == 1:
    p1 = pya.Point(center[0], center[1]+pin_length/2)
    p2 = pya.Point(center[0], center[1]-pin_length/2)
    
  pin = pya.Path([p1,p2],w)
  t = Trans(Trans.R0, center[0],center[1])
  text = Text (name, t)
  shape = cell.shapes(layer).insert(text)
  shape.text_size = 0.1
  cell.shapes(layer).insert(pin)

  return shape

class ebeam_pcell_directional_coupler(pya.PCellDeclarationHelper):

  def __init__(self):

    # Important: initialize the super class
    super(ebeam_pcell_directional_coupler, self).__init__()
    TECHNOLOGY = get_technology_by_name('SiEPICfab_EBeam_ZEP')

    # declare the parameters

    self.param("wg_width", self.TypeDouble, "Waveguides width", default = 0.5)
    self.param("gap", self.TypeDouble, "Coupling gap", default = 0.2)
    self.param("length", self.TypeDouble, "Coupling Length", default = 7)

    self.param("sbend_radius", self.TypeDouble, "S-Bend Radius", default = 15)
    self.param("sbend_height", self.TypeDouble, "S-Bend Height offset", default = 2)

    self.param("layer", self.TypeLayer, "Waveguide Layer", default = TECHNOLOGY['Si_core'])
    self.param("rib", self.TypeBoolean, "Rib waveguide?", default = True, hidden = True)
    self.param("layer_rib", self.TypeLayer, "Clad Layer", default = TECHNOLOGY['Si_clad'])
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'])

  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "ebeam_pcell_directional_coupler- width = %.3f - gap = %.3f - length = %.3f" % \
    (self.wg_width, self.gap, self.length)
  
  def coerce_parameters_impl(self):
    pass

  def can_create_from_shape(self, layout, shape, layer):
    return False
    
  def produce_impl(self):

    # fetch the parameters
    dbu = self.layout.dbu
    ly = self.layout
    shapes = self.cell.shapes

    shapes_wg = pya.Region()
    shapes_rib = pya.Region()

    LayerSiN = ly.layer(self.layer)
    LayerRib = ly.layer(self.layer_rib)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)

    from SiEPIC.extend import to_itype
    width = to_itype(self.wg_width,dbu)
    length = to_itype(self.length,dbu)
    gap = to_itype(self.gap,dbu)
    sbend_radius = to_itype(self.sbend_radius,dbu)
    sbend_height = to_itype(self.sbend_height,dbu)

    # Draw the coupling section
    y = gap/2 + width/2 # waveguides y center
    wg1 = Box(-length/2, y-width/2, length/2, y+width/2)
    wg2 = Box(-length/2, -y-width/2, length/2, -y+width/2)

    # insert shapes
    shapes_wg += wg1
    shapes_wg += wg2

    #shapes(LayerSiN).insert(wg1)
    #shapes(LayerSiN).insert(wg2)

    # Draw the S-bends
    from SiEPIC.utils.layout import layout_waveguide_sbend
    x1 = -length/2; y1 = y # top left
    shapes_wg += layout_waveguide_sbend(self.cell, LayerSiN, Trans(Trans.M90, x1,y1), width, sbend_radius, sbend_height, 0, insert = False)

    x2 = x1; y2 = -y # bottom left
    shapes_wg += layout_waveguide_sbend(self.cell, LayerSiN, Trans(Trans.R180, x2,y2), width, sbend_radius, sbend_height, 0, insert = False)

    x3 = -x1; y3 = y # top right
    shapes_wg += layout_waveguide_sbend(self.cell, LayerSiN, Trans(Trans.R0, x3,y3), width, sbend_radius, sbend_height, 0, insert = False)

    x4 = x3; y4 = -y # bottom right
    shapes_wg += layout_waveguide_sbend(self.cell, LayerSiN, Trans(Trans.M0, x4,y4), width, sbend_radius, sbend_height, 0, insert = False)


    # Draw the PinRec pins
    from SiEPIC._globals import PIN_LENGTH as pin_length
    from math import pi, cos, sin, log, sqrt, acos

    theta = acos(float(sbend_radius-abs(sbend_height/2))/sbend_radius)*180/pi
    x1_pin = x1-int(2*sbend_radius*sin(theta/180.0*pi))
    y1_pin = y1+sbend_height
    make_pin(self.cell, "opt1", [x1_pin,y1_pin], width, pin_length, LayerPinRecN)

    x2_pin = x1_pin
    y2_pin = -y1_pin
    make_pin(self.cell, "opt2", [x2_pin,y2_pin], width, pin_length, LayerPinRecN)

    x3_pin = -x1_pin
    y3_pin = y1_pin
    make_pin(self.cell, "opt3", [x3_pin,y3_pin], width, -pin_length, LayerPinRecN)

    x4_pin = -x1_pin
    y4_pin = -y1_pin
    make_pin(self.cell, "opt4", [x4_pin,y4_pin], width, -pin_length, LayerPinRecN)

    # Draw the DevRec box
    spacer = 6*width # Box extension beyond device area
    DevRecBox = Box(x1_pin, y1_pin+spacer, x4_pin, y4_pin-spacer)
    shapes(LayerDevRecN).insert(DevRecBox) 
    region_devrec = Region(DevRecBox)
    region_devrec2 = Region(DevRecBox).size(2000)


    # Draw the waveguide layer
    if self.rib == False:
      shapes(LayerSiN).insert(shapes_wg)
    else: # turn shape into a rib waveguide
      shapes_rib += shapes_wg
      shapeRib = shapes_rib.size(2000) - (region_devrec2-region_devrec)
      shapeCore = shapes_wg - (region_devrec2-region_devrec)

      shapes(LayerRib).insert(shapeRib)
      shapes(LayerSiN).insert(shapeCore)
      
    # Compact model information
    text_size = 0.1/dbu
    t = Trans(Trans.R0, x1_pin, y2_pin-spacer)
    text = Text ('Lumerical_INTERCONNECT_library=Design kits/SiEPICfab_EBeam', t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = text_size

    t = Trans(Trans.R0, x1_pin, y2_pin-spacer+text_size)
    text = Text ('Component=ebeam_pcell_directional_coupler', t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = text_size

    t = Trans(Trans.R0, x1_pin, y2_pin-spacer+2*text_size)
    text = Text('Spice_param:wg_width=%.3g gap=%.3g coupling_length=%.3g' % (self.wg_width*1e-6, self.gap*1e-6, self.length*1e-6), t )
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = text_size