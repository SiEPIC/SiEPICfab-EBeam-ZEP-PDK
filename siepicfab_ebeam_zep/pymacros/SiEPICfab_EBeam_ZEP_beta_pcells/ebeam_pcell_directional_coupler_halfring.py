# Mustafa Hammood, 2023
# Adopted from EBeam PDK.

from . import *
from pya import *
import pya
from SiEPIC.utils import get_technology_by_name

class ebeam_pcell_directional_coupler_halfring(pya.PCellDeclarationHelper):
  """
  The PCell declaration for the ebeam_dc_halfring_straight.
  Consists of a half-ring with 1 waveguides.
  """

  def __init__(self):
    # Important: initialize the super class
    super(ebeam_pcell_directional_coupler_halfring, self).__init__()
    TECHNOLOGY = get_technology_by_name('SiEPICfab_EBeam_ZEP')

    # declare the parameters
    self.param("silayer", self.TypeLayer, "Si Layer", default = TECHNOLOGY['Si_core'])
    self.param("cladlayer", self.TypeLayer, "Cladding Layer", default = TECHNOLOGY['Si_clad'])
    self.param("r", self.TypeDouble, "Radius", default = 10)
    self.param("w", self.TypeDouble, "Waveguide Width", default = 0.5)
    self.param("g", self.TypeDouble, "Gap", default = 0.2)
    self.param("Lc", self.TypeDouble, "Coupler Length", default = 0.0)
    self.param("orthogonal_identifier", self.TypeInt, "Orthogonal identifier (1=TE, 2=TM)", default = 1)     
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'])
    self.param("textl", self.TypeLayer, "Text Layer", default = TECHNOLOGY['Text'])

  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "ebeam_pcell_directional_coupler_halfring(R=" + ('%.3f' % self.r) + ",g=" + ('%g' % (1000*self.g)) + ",Lc=" + ('%g' % (1000*self.Lc)) + ",orthogonal_identifier=" + ('%s' % self.orthogonal_identifier) + ")"

  def can_create_from_shape_impl(self):
    return False
    
  def produce_impl(self):
    # This is the main part of the implementation: create the layout

    from math import pi, cos, sin
    from SiEPIC.utils import arc_wg, arc_wg_xy
    from SiEPIC._globals import PIN_LENGTH

    # fetch the parameters
    dbu = self.layout.dbu
    ly = self.layout
    shapes = self.cell.shapes
    
    LayerSiN = ly.layer(self.silayer)
    LayerCladN = ly.layer(self.cladlayer)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
    TextLayerN = ly.layer(self.textl)

    w = int(round(self.w/dbu))
    r = int(round(self.r/dbu))
    g = int(round(self.g/dbu))
    Lc = int(round(self.Lc/dbu))

    # draw the half-circle
    x = 0
    y = r+w+g
    self.cell.shapes(LayerSiN).insert(arc_wg_xy(x-Lc/2, y, r, w, 180, 270))
    self.cell.shapes(LayerSiN).insert(arc_wg_xy(x+Lc/2, y, r, w, 270, 360))
    
    # Pins on the top side:
    pin = Path([Point(-r-Lc/2, y-PIN_LENGTH/2), Point(-r-Lc/2, y+PIN_LENGTH/2)], w)
    shapes(LayerPinRecN).insert(pin)
    t = Trans(Trans.R0, -r-Lc/2, y)
    text = Text ("opt2", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    pin = Path([Point(r+Lc/2, y-PIN_LENGTH/2), Point(r+Lc/2, y+PIN_LENGTH/2)], w)
    shapes(LayerPinRecN).insert(pin)
    t = Trans(Trans.R0, r+Lc/2, y)
    text = Text ("opt4", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    if Lc > 0:
      wg1 = Box(-Lc/2, -w/2+w+g, Lc/2, w/2+w+g)
      shapes(LayerSiN).insert(wg1)


    # Create the waveguide
    wg1 = Box(-r-2*w-w-Lc/2, -w/2, r+2*w+w+Lc/2, w/2)
    shapes(LayerSiN).insert(wg1)

    # Pins on the bus waveguide side:
    pin = Path([Point(-r-2*w-w+PIN_LENGTH/2-Lc/2, 0), Point(-r-2*w-w-PIN_LENGTH/2-Lc/2, 0)], w)
    shapes(LayerPinRecN).insert(pin)
    t = Trans(Trans.R0, -r-2*w-w-Lc/2, 0)
    text = Text ("opt1", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    pin = Path([Point(r+2*w+w-PIN_LENGTH/2+Lc/2, 0), Point(r+2*w+w+PIN_LENGTH/2+Lc/2, 0)], w)
    shapes(LayerPinRecN).insert(pin)
    t = Trans(Trans.R0, r+2*w+w+Lc/2, 0)
    text = Text ("opt3", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    # Merge all the waveguide shapes, to avoid any small gaps
    layer_temp = self.layout.layer(LayerInfo(913, 0))
    shapes_temp = self.cell.shapes(layer_temp)
    ShapeProcessor().merge(self.layout,self.cell,LayerSiN,shapes_temp,True,0,True,True)
    self.cell.shapes(LayerSiN).clear()
    shapes_SiN = self.cell.shapes(LayerSiN)
    ShapeProcessor().merge(self.layout,self.cell,layer_temp, shapes_SiN,True,0,True,True)
    self.cell.shapes(layer_temp).clear()

    # Create the device recognition layer -- make it 1 * wg_width away from the waveguides.
    dev = Box(-r-2*w-w-Lc/2, -4*w-w, r+2*w+w+Lc/2, y )
    shapes(LayerDevRecN).insert(dev)

    # create cladding layer
    shapeClad = pya.Region()
    shapeClad += shapes_SiN
    region_devrec = Region(dev)
    region_devrec2 = Region(dev).size(2500)
    shapeClad = shapeClad.size(2000) - (region_devrec2-region_devrec)
    shapes(LayerCladN).insert(shapeClad)

    # Compact model information
    t = Trans(Trans.R0, -r, 0)
    text = Text ("Lumerical_INTERCONNECT_library=Design kits/SiEPICfab_EBeam", t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = self.r*0.03/dbu

    t = Trans(Trans.R0, -r, r/4)
    text = Text ('Component=ebeam_pcell_directional_coupler_halfring', t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = self.r*0.03/dbu

    t = Trans(Trans.R0, -r, r/2)
    text = Text ('Spice_param:wg_width=%.3g gap=%.3g radius=%.3g Lc=%.3g orthogonal_identifier=%s'% (self.w*1e-6,self.g*1e-6,self.r*1e-6,self.Lc*1e-6, self.orthogonal_identifier), t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = self.r*0.03/dbu

    print("Done drawing the layout for - ebeam_pcell_directional_coupler_halfring: %.3f-%g" % ( self.r, self.g) )
