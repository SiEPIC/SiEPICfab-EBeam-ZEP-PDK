from . import *
import pya
from pya import *
import math


class ebeam_pcell_nanobeam_cavity(pya.PCellDeclarationHelper):
  """
  Input: length, width
  """
  
  def __init__(self):
  
    # Important: initialize the super class
    super(ebeam_pcell_nanobeam_cavity, self).__init__()
    from SiEPIC.utils import get_technology_by_name, load_Waveguides_by_Tech
  
    self.technology_name = 'SiEPICfab_EBeam_ZEP'
    TECHNOLOGY = get_technology_by_name(self.technology_name)
    self.TECHNOLOGY = TECHNOLOGY
             
    # Load all strip waveguides
    waveguide_types = load_Waveguides_by_Tech(self.technology_name)   
        
    self.param("w", self.TypeDouble, "Waveguide width (microns)", default = 0.5)     
    self.param("s", self.TypeDouble, "Cavity length (microns)", default = 0.56)
    self.param("n_max_b", self.TypeInt, "Number of unchanged holes (back reflector)", default = 9)          
    self.param("n_taper_b", self.TypeInt, "Number of tapered holes back", default = 4)          
    self.param("n_taper_f", self.TypeInt, "2 x Number of taper holes per side (front reflector)", default = 4)     
    self.param("n_max_f", self.TypeInt, "Number of central max-radius holes (front reflector)", default = 1)
    self.param("r_max_b", self.TypeDouble, "maximum radius on back reflector", default = 100)
    self.param("r_min", self.TypeDouble, "minimum radius", default = 50)
    self.param("r_max_f", self.TypeDouble, "maximum radius on front reflector", default = 70)     

    self.param("pitch_scale", self.TypeDouble, "linear pitch scale (the m in y=mx+b) (unitless)", default=1.22)
    self.param("pitch_offset", self.TypeDouble, "linear pitch offset (the b in y=mx+b) (in nm)", default=308)
    self.param("n_vertices", self.TypeInt, "Vertices of a hole", default = 32)
    self.param("n_type", self.TypeInt, "1 if ZEP, 0 if HSQ", default = 0)  
    self.param("layer", self.TypeLayer, "Layer - Waveguide", default = TECHNOLOGY['Si_core'])
    self.param("cladlayer", self.TypeLayer, "Cladding Layer", default = TECHNOLOGY['Si_clad'])
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'])
    self.param("etch", self.TypeLayer, "oxide etch layer", default = TECHNOLOGY['Si_etch_highres'])
    self.param("extra_Si",self.TypeLayer, "Extra Si Layer", default = TECHNOLOGY['Si_etch_highres'])

  def display_text_impl(self):
    return "nanobeam_cavity_%.2f_%.2f" % (self.w, self.s)
  

  def coerce_parameters_impl(self):
    pass

  def can_create_from_shape(self, layout, shape, layer):
    return False
    
  def produce_impl(self):
    # fetch the parameters
    dbu = self.layout.dbu
    ly = self.layout
    shapes = self.cell.shapes

    LayerSi = self.layer
    LayerSiN = ly.layer(LayerSi)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
    LayerCladN = ly.layer(self.cladlayer)
    LayerEtch = ly.layer(self.etch)
    LayerHighResHoles = ly.layer(self.extra_Si)

    # Fetch all the parameters:
    s = self.s/dbu
    w = self.w/dbu
    n_max_f = self.n_max_f                 # number of central max-radius holes (front)
    n_taper_f = self.n_taper_f                 # number of taper holes per side (front)
    n_taper_b = self.n_taper_b
    n_max_b = self.n_max_b
    r_max_b = self.r_max_b
    r_min = self.r_min
    r_max_f = self.r_max_f    
    n_vertices = self.n_vertices
    n_type = self.n_type
    pitch_scale = self.pitch_scale
    pitch_offset = self.pitch_offset
  
    # function to generate points to create a circle
    def circle(x,y,r):
      npts = n_vertices
      theta = 2 * math.pi / npts # increment, in radians
      pts = []
      for i in range(0, npts):
        pts.append(Point.from_dpoint(DPoint((x+r*math.cos(i*theta))/1, (y+r*math.sin(i*theta))/1)))
      return pts

    def linspace(start, stop, num):
      step = (stop - start) / (num - 1)
      return [start + step * i for i in range(num)]

    # raster through all holes with shifts and waveguide 
    hole = Region()
    
    # ------------------------------------------------------------
    # Radii of all circles from back to front reflector
    # ------------------------------------------------------------

    # Back reflector: unchanged
    r_list1 = linspace(r_max_b, r_max_b, n_max_b - 1)
    r_list2 = linspace(r_max_b, r_min, n_taper_b + 1)

    # Front reflector: symmetric taper-up / center / taper-down
    # n_taper_f = number of taper holes per side
    # n_max_f = number of central max-radius (r_max_f) holes
    n_taper = int(n_taper_f)
    n_center = int(n_max_f)

    # Build taper from r_min -> r_max_f (exclude the final r_max_f to avoid duplication)
    r_taper = []
    if n_taper > 0:
      r_taper_full = linspace(r_min, r_max_f, n_taper + 1)  # length n_taper+1
      r_taper = r_taper_full[0:n_taper]                   # length n_taper, no duplicate r_max_f

    # Center flat region at maximum radius
    r_center = [r_max_f] * max(n_center, 0)

    # Symmetric front reflector radii: [taper up] + [center] + [taper down]
    r_front = []
    r_front.extend(r_taper)
    r_front.extend(r_center)
    r_front.extend(r_taper[::-1])

    # Combine all radii: back (r_list1, r_list2) + front (r_front)
    r = []
    r.extend(r_list1)
    r.extend(r_list2)
    r.extend(r_front)
    
    # ------------------------------------------------------------
    # Position of circles on positive x, front reflector
    # ------------------------------------------------------------

    x_pos = []
    n_front = len(r_front)
    if n_front > 0:
      # allocate zeros to avoid division-by-zero in linspace if n_front == 1
      x_pos = [0] * n_front
      # first front hole is at s/2 from cavity center
      x_pos[0] = s/2
      # spacing based on previous hole radius (same rule as original)
      for i in range(1, n_front):
        x_pos[i] = x_pos[i-1] + pitch_scale * r_front[i-1] + pitch_offset

    # ------------------------------------------------------------
    # Position of circles on negative x, back reflector (unchanged)
    # ------------------------------------------------------------

    x_list3 = linspace(0,0,n_taper_b)
    x_list3[0] = s/2 
    
    # flip r_list2
    r_list2_flipped = r_list2[::-1]
    for i in range(1, n_taper_b):
        x_list3[i] = x_list3[i-1] + pitch_scale * r_list2_flipped[i-1] + pitch_offset

    x_list4 = linspace(0,0,n_max_b + 1)
    x_list4[0] = x_list3[n_taper_b - 1]
    x_list4[1] = x_list4[0] + pitch_scale * r_list2_flipped[n_taper_b-1] + pitch_offset
    for i in range(2, n_max_b):
        x_list4[i] = x_list4[i-1] + pitch_scale * r_list1[i-1] + pitch_offset
    x_list4[n_max_b] = x_list4[n_max_b-1] + pitch_scale * r_max_b + pitch_offset

    x_full = []
    x_full.extend(x_list3)
    x_full.extend(x_list4[1::])
    x_full_rev = x_full[::-1]
    
    # multiply by -1 for negative side
    x_neg = linspace(0,0, len(x_full_rev))
    for i in range(0, len(x_full_rev)):
       x_neg[i] = -1 * x_full_rev[i]

    # ALL x positions: negative to positive
    x_all = []
    x_all.extend(x_neg)
    x_all.extend(x_pos)
    
    # ------------------------------------------------------------
    # Place all holes
    # ------------------------------------------------------------
    for i in range(0, len(r)):
        hole_cell = circle(0,0,r[i])
        hole_poly = Polygon(hole_cell)  
        hole_x = x_all[i]
        hole_y = 0
        hole_trans = Trans(Trans.R0,hole_x,hole_y)
        hole_t = hole_poly.transformed(hole_trans)
        hole.insert(hole_t)  
        self.cell.shapes(LayerHighResHoles).insert(hole) 

    if n_type == 1:      
      trench_length = round(hole_x*2+16.666/dbu)
      trench_width = 2/dbu #5 microns
      trench_x = trench_length/2
      trench1_y1 = w/2
      trench1_y2 = w/2+trench_width
      trench = Region()
      trench.insert(Box(-trench_x,trench1_y1,trench_x,trench1_y2))
      trench.insert(Box(-trench_x,-trench1_y1,trench_x,-trench1_y2))
      phc = trench
      self.cell.shapes(LayerSiN).insert(phc)
      phc = trench + hole
      
    if n_type == 0:      
      Si_slab = Region()
      beam_l = hole_x*2+16.666/dbu
      beam_x = beam_l/2
      Si_slab.insert(Box(-beam_x, -w/2,beam_x,w/2))
      anchor_l = 8/dbu
      phc = Si_slab
      self.cell.shapes(LayerSiN).insert(phc)
      
        #add the left bus pin
    xp1 = -0.05/self.layout.dbu
    xp2 = 0.05/self.layout.dbu
    yp1 = 0
    xa = -beam_x
    xb = beam_x
    p1 = [Point(xa+xp2,yp1),Point(xa+xp1,yp1)]
    p1c = Point(xa,yp1)
    self.set_p1 = p1c
    self.p1 = p1c


    pin = Path(p1,w)
    shapes(LayerPinRecN).insert(pin)
    t = Trans(Trans.R0,xa,yp1)
    text = Text("opt1",t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu  
  
    
    #add the right bus pin
    p2 = [Point(xb+xp1,yp1),Point(xb+xp2,yp1)]
    p2c = Point(xb,yp1)
    self.set_p2 = p2c
    self.p2 = p2c


    pin = Path(p2,w)
    shapes(LayerPinRecN).insert(pin)
    t = Trans(Trans.R0,xb,yp1)
    text = Text("opt2",t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    layer_temp = self.layout.layer(LayerInfo(913, 0))
    shapes_temp = self.cell.shapes(layer_temp)
    ShapeProcessor().merge(self.layout,self.cell,LayerSiN,shapes_temp,True,0,True,True)
    self.cell.shapes(LayerSiN).clear()
    shapes_SiN = self.cell.shapes(LayerSiN)
    ShapeProcessor().merge(self.layout,self.cell,layer_temp, shapes_SiN,True,0,True,True)
    self.cell.shapes(layer_temp).clear()
    
    # w = int(round(self.w/dbu))
    dev = Box(xa, -w*2, xb, w*2 )
    shapes(LayerDevRecN).insert(dev)

    shapeClad = pya.Region()
    shapeClad += shapes_SiN
    region_devrec = Region(dev)
    region_devrec2 = Region(dev).size(2500)
    shapeClad = shapeClad.size(2000) - (region_devrec2-region_devrec)
    shapes(LayerCladN).insert(shapeClad)
