from . import *
import pya
from pya import *
import math

class ebeam_waveguide_spiral(pya.PCellDeclarationHelper):
  """
  Input: 
  """

  def __init__(self, tech, wg_option):

    from SiEPIC.utils import   load_Waveguides_by_Tech 
    # Important: initialize the super class
    super(ebeam_waveguide_spiral, self).__init__()
    self.tech_name = tech
    TECHNOLOGY = get_technology_by_name(self.tech_name)
    self.waveguides =  load_Waveguides_by_Tech(self.tech_name)
    self.optionList = [waveguide['name'] for waveguide in self.waveguides]
    self.optionsParameter = list(zip(self.optionList, self.optionList))

    # declare the parameters
    self.param("length", self.TypeDouble, "Target Waveguide length", default = 10.0)     
    #self.param("wg_width", self.TypeDouble, "Waveguide width (microns)", default = 0.5)     
    self.param("min_radius", self.TypeDouble, "Minimum radius (microns)", default = 5)     
    self.param("wg_spacing", self.TypeDouble, "Waveguide spacing (microns)", default = 1)     
    self.param("spiral_ports", self.TypeInt, "Ports on the same side? 0/1", default = 0)
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'], hidden = True)
    self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'], hidden = True)
    self.param("option", self.TypeString, "WG Option", default =  wg_option, choices = (self.optionsParameter) )
    self.param("text", self.TypeLayer, "Text Layer", default = TECHNOLOGY['Text'], hidden = True)
    self.param("cover_layers", self.TypeList, "Cover Layers", default = [])
    self.param("cover_extent", self.TypeList, "Cover Layer extents", default =  [])
    self.param("CML", self.TypeString, "CML", default = 'SiEPIC_EBeam_PDK', hidden = True)
    self.param("model", self.TypeString, "model", default = 'WG_Spiral', hidden = True)
    
  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "spiral_%.1f-%.1f-%.1f" % \
    (self.length, self.min_radius, self.wg_spacing)
  
  def coerce_parameters_impl(self):
    print("SiEPICfab_EBeam_ZEP.ebeam_waveguide_spiral coerce parameters")
        
    if 0:
        TECHNOLOGY = get_technology_by_name(self.tech_name)

  def can_create_from_shape(self, layout, shape, layer):
    return False
    
  def produce_impl(self):
    from SiEPIC.utils import arc_wg, arc_wg_xy, arc_to_waveguide, points_per_circle
    from SiEPIC.extend import to_itype

    TECHNOLOGY = get_technology_by_name(self.tech_name) 
    
    # fetch the parameters
    dbu = self.layout.dbu
    ly = self.layout
    shapes = self.cell.shapes

    # get the waveguide information
    waveguide = [wg for wg in self.waveguides if wg['name'] ==  self.option ][0]   
    params = {
              'width': 0,
              'wgs': []}   
 
              
    for component in waveguide['component']:
        params['wgs'].append({'layer': component['layer'], 'width': float(component['width']), 'offset': float(component['offset'])})
        w = (params['wgs'][-1]['width'] / 2 + params['wgs'][-1]['offset']) * 2

    self.wg_width = float(waveguide['width'])   
    self.CML = waveguide['CML']
    self.model = waveguide['model']     
    #print(params)    

    self.layers = [wg['layer'] for wg in params['wgs']]
    self.widths = [wg['width'] for wg in params['wgs']]
    self.offsets = [wg['offset'] for wg in params['wgs']]
    
    if not ( 'Waveguide' in self.layers):
      self.layers.append('Waveguide')
      self.widths.append(self.wg_width)
      self.offsets.append(0)
      

    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
    LayerTextN = ly.layer(self.text)
    
    for lr in range(0, len(self.layers)): 
      if ('DevRec' != self.layers[lr] ): 
        wg_layer = self.layout.layer(TECHNOLOGY[self.layers[lr]]) 
        w = self.widths[lr]
        offset = self.offsets[lr]      
        # draw spiral
        from math import pi, cos, sin, log, sqrt
        
        # Archimedes spiral
        # r = b + a * theta
        b = self.min_radius
        spacing = self.wg_spacing+self.wg_width;
        a = 2*spacing/(2*pi)


        # area, length, turn tracking for spiral
        area = 0
        spiral_length = 0
        turn = -1
        
        while spiral_length < self.length:
          turn +=1

          # Spiral #1
          pts = []
          # local radius:
          r = 2*b + a * turn * 2 * pi - w/2 + offset
          # number of points per circle:
          npoints = int(points_per_circle(r))
          # increment, in radians, for each point:
          da = 2 * pi / npoints  
          # draw the inside edge of spiral
          for i in range(0, npoints+1):
            t = i*da
            xa = (a*t + r) * cos(t);
            ya = (a*t + r) * sin(t);
            pts.append(Point.from_dpoint(DPoint(xa/dbu, ya/dbu)))
          # draw the outside edge of spiral
          r = 2*b + a * turn * 2 * pi + w/2 + offset
          npoints = int(points_per_circle(r))
          da = 2 * pi / npoints  
          for i in range(npoints, -1, -1):
            t = i*da
            xa = (a*t + r) * cos(t);
            ya = (a*t + r) * sin(t);
            pts.append(Point.from_dpoint(DPoint(xa/dbu, ya/dbu)))
          polygon = Polygon(pts)
          area += polygon.area()
          shapes(wg_layer).insert(polygon)

          # Spiral #2
          pts = []
          # local radius:
          r = 2*b + a * turn * 2 * pi - w/2 - spacing + offset
          # number of points per circle:
          npoints = int(points_per_circle(r))
          # increment, in radians, for each point:
          da = 2 * pi / npoints  
          # draw the inside edge of spiral
          for i in range(0, npoints+1):
            t = i*da + pi
            xa = (a*t + r) * cos(t);
            ya = (a*t + r) * sin(t);
            pts.append(Point.from_dpoint(DPoint(xa/dbu, ya/dbu)))
          # draw the outside edge of spiral
          r = 2*b + a * turn * 2 * pi + w/2  - spacing + offset
          npoints = int(points_per_circle(r))
          da = 2 * pi / npoints  
          for i in range(npoints, -1, -1):
            t = i*da + pi
            xa = (a*t + r) * cos(t);
            ya = (a*t + r) * sin(t);
            pts.append(Point.from_dpoint(DPoint(xa/dbu, ya/dbu)))
          polygon = Polygon(pts)
          area += polygon.area()
          shapes(wg_layer).insert(polygon)

          # waveguide length:
          spiral_length = area / w * dbu*dbu + 2 * pi * self.min_radius

        if self.spiral_ports:
          # Spiral #1 extra 1/2 arm
          turn = turn + 1
          pts = []
          # local radius:
          r = 2*b + a * turn * 2 * pi - w/2 +offset
          # number of points per circle:
          npoints = int(points_per_circle(r))
          # increment, in radians, for each point:
          da = pi / npoints  
          # draw the inside edge of spiral
          for i in range(0, npoints+1):
            t = i*da
            xa = (a*t + r) * cos(t);
            ya = (a*t + r) * sin(t);
            pts.append(Point.from_dpoint(DPoint(xa/dbu, ya/dbu)))
          # draw the outside edge of spiral
          r = 2*b + a * turn * 2 * pi + w/2 + offset
          npoints = int(points_per_circle(r))
          da = pi / npoints  
          for i in range(npoints, -1, -1):
            t = i*da
            xa = (a*t + r) * cos(t);
            ya = (a*t + r) * sin(t);
            pts.append(Point.from_dpoint(DPoint(xa/dbu, ya/dbu)))
          polygon = Polygon(pts)
          area += polygon.area()
          shapes(wg_layer).insert(polygon)
          turn = turn - 1
          # waveguide length:
          spiral_length = area / self.wg_width * dbu*dbu + 2 * pi * self.min_radius

        # Centre S-shape connecting waveguide        
        #layout_arc_wg_dbu(self.cell, LayerSiN, -b/dbu, 0, b/dbu, self.wg_width/dbu, 0, 180)
        self.cell.shapes(wg_layer).insert(arc_wg_xy(-b/dbu, 0, (b+offset)/dbu, w/dbu, 0, 180))
        #layout_arc_wg_dbu(self.cell, LayerSiN, b/dbu, 0, b/dbu, self.wg_width/dbu, 180, 0)
        self.cell.shapes(wg_layer).insert(arc_wg_xy(b/dbu, 0, (b+offset)/dbu, w/dbu, 180, 0))
    
    print("spiral length: %s microns" % spiral_length)

    # Pins on the waveguide:
    pin_length = 0.02/dbu
    
    x = -(2*b + a * (turn+1) * 2 * pi)/dbu
    w = self.wg_width / dbu
    t = Trans(Trans.R0, x,0)
    pin = Path([Point(0,pin_length/2), Point(0,-pin_length/2)], w)
    pin_t = pin.transformed(t)
    shapes(LayerPinRecN).insert(pin_t)
    text = Text ("pin2", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    if self.spiral_ports:
      x = -(2*b + a * (turn+1.5) * 2 * pi)/dbu
      pin = Path([Point(0,pin_length/2), Point(0,-pin_length/2)], w)
    else:
      x = (2*b + a * (turn+1) * 2 * pi)/dbu
      pin = Path([Point(0,-pin_length/2), Point(0,pin_length/2)], w)
    t = Trans(Trans.R0, x,0)
    pin_t = pin.transformed(t)
    shapes(LayerPinRecN).insert(pin_t)
    text = Text ("pin1", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    # Compact model information
    t = Trans(Trans.R0, -abs(x), 0)
    text = Text ('Length=%.3fu' % spiral_length, t)
    shape = shapes(LayerTextN).insert(text)
    shape.text_size = abs(x)/8
    t = Trans(Trans.R0, 0, 0)
    text = Text ('Lumerical_INTERCONNECT_library='+self.CML, t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = 0.1/dbu
    t = Trans(Trans.R0, 0, w*2)
    text = Text ('Component='+self.model, t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = 0.1/dbu
    t = Trans(Trans.R0, 0, -w*2)
    text = Text \
      ('Spice_param:wg_length=%.3fu wg_width=%.3fu min_radius=%.3fu wg_spacing=%.3fu' %\
      (spiral_length, self.wg_width, (self.min_radius), self.wg_spacing), t )
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = 0.1/dbu

    # Create the device recognition layer -- make it 1 .5* wg_width away from the waveguides.
    x = abs(x)
    npoints = int(points_per_circle(x) /10 )
    da = 2 * pi / npoints # increment, in radians
    r=x + 3 * self.wg_width/dbu
    pts = []
    for i in range(0, npoints+1):
      pts.append(Point.from_dpoint(DPoint(r*cos(i*da), r*sin(i*da))))
    shapes(LayerDevRecN).insert(Polygon(pts))
    

    # Create cover layers
    if not (len(self.cover_layers)==len(self.cover_extent)) :
      raise Exception("There must be an equal number of cover layers and cover layer extent")
    for lr in range(0, len(self.cover_layers)):
      if self.cover_layers[lr].strip() != '':
        layer = self.layout.layer(TECHNOLOGY[self.cover_layers[lr].strip()])      
        extent = int(float(self.cover_extent[lr].strip())/dbu)
        r=x + extent
        pts = []
        for i in range(0, npoints+1):
          pts.append(Point.from_dpoint(DPoint(r*cos(i*da), r*sin(i*da))))
        shapes(layer).insert(Polygon(pts))

    print("spiral done.")