from . import *
from pya import *

class clipp_side(pya.PCellDeclarationHelper):
  """
  The PCell declaration for the CLIPP 
   - Contactless Integrated Photonic Probes
   - studied extensively by Andrea Melloni's group in Italy
  Variant:
   - side or top: the metal capacitor is on the side of the waveguide
       (if the process does not have oxide), 
       or on top if there is oxide
   - etch silicon under metal pads
  by Lukas Chrostowski, 2021, copyright
  MIT license.
  """

  def __init__(self):

    # Important: initialize the super class
    super(clipp_side, self).__init__()
    TECHNOLOGY = get_technology_by_name('SiEPICfab_EBeam_ZEP')

    # declare the parameters
    self.param("silayer", self.TypeLayer, "Si Layer", default = TECHNOLOGY['Si_core'])
    self.param("clad", self.TypeLayer, "Cladding Layer", default = TECHNOLOGY['Si_clad'])
    self.param("wg_width", self.TypeDouble, "Waveguide Width", default = 0.5)
    self.param("clad_width", self.TypeDouble, "Cladding Width", default = 2)
    self.param("mlayer", self.TypeLayer, "Metal Layer", default = TECHNOLOGY['M1'])
    self.param("m_clipp_width", self.TypeDouble, "Metal CLIPP Width", default = 5)
    self.param("m_clipp_wg_offset", self.TypeDouble, "Metal CLIPP Offset from waveguide", default = 3)
    self.param("m_si_offset", self.TypeDouble, "Metal to Silicon offset", default = 5)
    self.param("m_clipp_pitch", self.TypeDouble, "Metal CLIPP pitch", default = 300)
    self.param("m_clipp_length", self.TypeDouble, "Metal CLIPP length", default = 200)
    self.param("m_clipp_contactlength", self.TypeDouble, "Metal CLIPP contact length", default = 20)
    self.param("m_clipp_contactwidth", self.TypeDouble, "Metal CLIPP contact width", default = 5)
    self.param("m_padsize", self.TypeDouble, "Metal pad size", default = 100)
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'])
    # hidden parameters, can be used to query this component:
    self.param("p1", self.TypeShape, "DPoint location of pin1", default = Point(-10000, 0), hidden = True, readonly = True)
    self.param("p2", self.TypeShape, "DPoint location of pin2", default = Point(0, 10000), hidden = True, readonly = True)
    

  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "clipp_side(R=" + ('%.3f-%.3f-%.3f' % (self.wg_width,self.wg_width,self.m_clipp_length) ) + ")"

  def can_create_from_shape_impl(self):
    return False


  def produce(self, layout, layers, parameters, cell):
    """
    coerce parameters (make consistent)
    """
    self._layers = layers
    self.cell = cell
    self._param_values = parameters
    self.layout = layout
    shapes = self.cell.shapes


    # cell: layout cell to place the layout
    # LayerSiN: which layer to use
    # w: waveguide width
    # length units in dbu

    # fetch the parameters
    dbu = self.layout.dbu
    ly = self.layout
    
    LayerSi = self.silayer
    LayerSiN = self.silayer_layer
    LayerSiClad = self.clad_layer
    LayerM = self.mlayer_layer
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
    
    w = int(round(self.wg_width/dbu))
    clad_width = int(round(self.clad_width/dbu))
    m_si_offset = int(round(self.m_si_offset/dbu))
    length = int(round(max(self.m_padsize,self.m_clipp_length)/dbu+self.m_clipp_pitch/dbu))+m_si_offset*2

    m_clipp_width = int(round(self.m_clipp_width/dbu))
    m_clipp_wg_offset = int(round(self.m_clipp_wg_offset/dbu))
    m_clipp_pitch = int(round(self.m_clipp_pitch/dbu))
    m_clipp_length = int(round(self.m_clipp_length/dbu))
    m_clipp_contactlength = int(round(self.m_clipp_contactlength/dbu))
    m_clipp_contactwidth = int(round(self.m_clipp_contactwidth/dbu))
    m_padsize = int(round(self.m_padsize/dbu))
    
    # waveguide core
    pts = [Point(length/2,0), Point(-length/2,0)]
    shapes(LayerSiN).insert(Path(pts, w))

    # waveguide cladding
    clad_region = Region(Path(pts, w+clad_width*2))

    # metal CLIPP
    # left one:
    y = -w/2-m_clipp_wg_offset-m_clipp_width/2
    pts = [Point(-m_clipp_pitch/2-m_clipp_length/2,y), Point(-m_clipp_pitch/2+m_clipp_length/2,y)]
    shapes(LayerM).insert(Path(pts, m_clipp_width))
    pts = [Point(-m_clipp_pitch/2-m_clipp_length/2-m_si_offset,y), Point(-m_clipp_pitch/2+m_clipp_length/2+m_si_offset,y)]
    clad_region += Region(Path(pts, m_clipp_width+m_si_offset*2))
    # right one:
    pts = [Point(m_clipp_pitch/2-m_clipp_length/2,y), Point(m_clipp_pitch/2+m_clipp_length/2,y)]
    shapes(LayerM).insert(Path(pts, m_clipp_width))
    pts = [Point(m_clipp_pitch/2+m_clipp_length/2+m_si_offset,y), Point(m_clipp_pitch/2-m_clipp_length/2-m_si_offset,y)]
    clad_region += Region(Path(pts, m_clipp_width+m_si_offset*2))

    # metal CLIPP contact
    # left one:
    y += -m_clipp_width/2
    pts = [Point(-m_clipp_pitch/2,y), Point(-m_clipp_pitch/2,y-m_clipp_contactlength)]
    shapes(LayerM).insert(Path(pts, m_clipp_width))
    clad_region += Region(Path(pts, m_clipp_width+m_si_offset*2))
    # right one:
    pts = [Point(m_clipp_pitch/2,y), Point(m_clipp_pitch/2,y-m_clipp_contactlength)]
    shapes(LayerM).insert(Path(pts, m_clipp_width))
    clad_region += Region(Path(pts, m_clipp_width+m_si_offset*2))
    
    # probe pad
    # left one:
    y = -w/2-m_clipp_wg_offset-m_clipp_width-m_clipp_contactlength
    pts = [Point(-m_clipp_pitch/2,y), Point(-m_clipp_pitch/2,y-m_padsize)]
    shapes(LayerM).insert(Path(pts, m_padsize).simple_polygon())
    pts = [Point(-m_clipp_pitch/2,y+m_si_offset), Point(-m_clipp_pitch/2,y-m_padsize-m_si_offset)]
    clad_region += Region(Path(pts, m_padsize+m_si_offset*2))
    # right one:
    pts = [Point(m_clipp_pitch/2,y), Point(m_clipp_pitch/2,y-m_padsize)]
    shapes(LayerM).insert(Path(pts, m_padsize).simple_polygon())
    pts = [Point(m_clipp_pitch/2,y+m_si_offset), Point(m_clipp_pitch/2,y-m_padsize-m_si_offset)]
    clad_region += Region(Path(pts, m_padsize+m_si_offset*2))
    
    # cladding layer:
    shapes(LayerSiClad).insert(clad_region.merge())

    # Create the pins on the waveguides, as short paths:
    from SiEPIC._globals import PIN_LENGTH as pin_length
    
    # Pin on the left side:
    p1 = [Point(-length/2+pin_length/2,0), Point(-length/2-pin_length/2,0)]
    p1c = Point(-length/2,0)
    self.set_p1 = p1c
    self.p1 = p1c
    pin = Path(p1, w)
    shapes(LayerPinRecN).insert(pin)
    t = Trans(Trans.R0, -length/2, 0)
    text = Text ("pin1", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    # Pin on the right side:
    p2 = [Point(length/2-pin_length/2,0), Point(length/2+pin_length/2,0)]
    p2c = Point(length/2, 0)
    self.set_p2 = p2c
    self.p2 = p2c
    pin = Path(p2, w)
    shapes(LayerPinRecN).insert(pin)
    t = Trans(Trans.R0, length/2, 0)
    text = Text ("pin2", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu
    shape.text_halign = 2

    # Create the device recognition layer -- make it 1 * wg_width away from the waveguides.
#    pts = [Point(length/2,0), Point(-length/2,0)]
#    shapes(LayerDevRecN).insert(Path(pts, w+w*2+clad_width*2).simple_polygon())
    shapes(LayerDevRecN).insert(clad_region.merge())

    # Compact model information
    '''
    t = Trans(Trans.R0, w/10, 0)
    text = Text ("Lumerical_INTERCONNECT_library=Design kits/ebeam", t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = length/100
    t = Trans(Trans.R0, length/10, w/4)
    text = Text ('Component=ebeam_taper_te1550', t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = length/100
    t = Trans(Trans.R0, length/10, w/2)
    text = Text ('Spice_param:wg_width=%.3fu wg_length=%.3fu'% (self.wg_width,dbu*length), t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = length/100
    '''

    return "clipp_side(" + ('%.3f-%.3f-%.3f' % (self.wg_width,self.wg_width,length) ) + ")"
