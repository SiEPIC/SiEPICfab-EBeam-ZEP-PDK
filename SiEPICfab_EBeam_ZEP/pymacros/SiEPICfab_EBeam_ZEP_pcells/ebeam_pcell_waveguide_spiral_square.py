from . import *
import pya
from pya import *
import math

class ebeam_pcell_waveguide_spiral_square(pya.PCellDeclarationHelper):


  def __init__(self, tech, wg_option):

    from SiEPIC.utils import   load_Waveguides_by_Tech 
    # Important: initialize the super class
    super(ebeam_pcell_waveguide_spiral_square, self).__init__()
    self.tech_name = tech
    TECHNOLOGY = get_technology_by_name(self.tech_name)
    self.waveguides =  load_Waveguides_by_Tech(self.tech_name)
    self.optionList = [waveguide['name'] for waveguide in self.waveguides]
    self.optionsParameter = list(zip(self.optionList, self.optionList))

    # declare the parameters
    self.param("l", self.TypeDouble, "Length of Innermost WG", default = 300.0)     
    #self.param("wg_width", self.TypeDouble, "Waveguide width (microns)", default = 0.48)     
    self.param("r0", self.TypeDouble, "Radius (microns)", default = 5)     
    self.param("s", self.TypeDouble, "Waveguide spacing (microns)", default = 1)     
    self.param("spiral_ports", self.TypeInt, "Ports on the side? 0/1", default = 1)
    self.param("nsp", self.TypeInt, "Number of Spirals", default = 10)
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'], hidden = True)
    self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'], hidden = True)
    self.param("option", self.TypeString, "WG Option", default = wg_option, choices = (self.optionsParameter) )
    self.param("text", self.TypeLayer, "Text Layer", default = TECHNOLOGY['Text'], hidden = True)
    self.param("CML", self.TypeString, "CML", default = 'AIMPhotonics', hidden = True)
    self.param("model", self.TypeString, "model", default = 'WG_ebeam_pcell_waveguide_spiral_square', hidden = True)
        
  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "ebeam_pcell_waveguide_spiral_square"
  
  def coerce_parameters_impl(self):
    print("AIMPhotonics_PDK.ebeam_pcell_waveguide_spiral_square coerce parameters")
    
    if 0:
        TECHNOLOGY = get_technology_by_name(self.tech_name)

  def can_create_from_shape(self, layout, shape, layer):
    return False
    
  def produce_impl(self):
    from SiEPIC.utils import arc_wg, arc_wg_xy, points_per_circle
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
    
    r0 = to_itype(self.r0,dbu)
    l = to_itype(self.l,dbu)
    spacing = to_itype(self.s+self.wg_width,dbu)  
    spiral_length = 0  
    
    for lr in range(0, len(self.layers)):  
      if ('DevRec' != self.layers[lr] ):     
        wg_layer = self.layout.layer(TECHNOLOGY[self.layers[lr]]) 
        w = to_itype(self.widths[lr],dbu)
        offset = to_itype(self.offsets[lr],dbu)      
        # draw spiral
        from math import pi, cos, sin, log, sqrt
   
        # area, length, turn tracking for spiral

        turn = -1
        
        # the center line
        pts = []
        pts.append(pya.Point.from_dpoint(pya.DPoint(-w/2, -l/2)))
        pts.append(pya.Point.from_dpoint(pya.DPoint(-w/2, l/2)))
        pts.append(pya.Point.from_dpoint(pya.DPoint(w/2, l/2)))
        pts.append(pya.Point.from_dpoint(pya.DPoint(w/2, -l/2)))
        line = pya.Polygon(pts)
        t = Trans(Trans.R0,offset, 0)
        self.cell.shapes(wg_layer).insert(line.transformed(t))
        
        if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + self.l
        
        # the top half circle
        xo=r0
        yo=l/2        
        r = r0 + offset         
        t = Trans(Trans.R0,xo, yo)
        self.cell.shapes(wg_layer).insert(arc_wg(r, w, 90., 180.).transformed(t))
        
        # the bottom half circle
        xo=-r0
        yo=-l/2        
        r = r0 + offset         
        t = Trans(Trans.R0,xo, yo)
        self.cell.shapes(wg_layer).insert(arc_wg(r, w, 270., 360.).transformed(t)) 
        
        if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + ( pi * r0) * dbu
        
        while turn < self.nsp-2:
            turn +=1

            # top right corner
            xo=r0+(turn)*(spacing)
            yo=l/2+(turn)*(spacing)        
            r = r0 + offset         
            t = Trans(Trans.R0,xo, yo)
            self.cell.shapes(wg_layer).insert(arc_wg(r, w, 0., 90.).transformed(t))
            if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + (1/2 * pi * r0) * dbu

            # right lines
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint(-w/2, -yo-spacing)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(-w/2, yo)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(w/2, yo)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(w/2, -yo-spacing)))
            line = pya.Polygon(pts)
            t = Trans(Trans.R0,xo+r, 0)
            self.cell.shapes(wg_layer).insert(line.transformed(t))
            if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + abs(2 * yo + spacing) * dbu
                
            # bottom right corner
            xo=r0+(turn)*(spacing)
            yo=-l/2-(turn+1)*(spacing)        
            r = r0 + offset         
            t = Trans(Trans.R0,xo, yo)
            self.cell.shapes(wg_layer).insert(arc_wg(r, w, 270., 360.).transformed(t))
            if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + (1/2 * pi * r0) * dbu

            # bottom lines
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint(xo, -w/2)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(-xo-spacing,-w/2)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(-xo-spacing,w/2)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(xo,w/2)))
            line = pya.Polygon(pts)
            t = Trans(Trans.R0,0, yo-r)
            self.cell.shapes(wg_layer).insert(line.transformed(t))          
            if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + abs(2 * xo + spacing) * dbu
                
            # bottom left corner
            xo=-r0-(turn)*(spacing)
            yo=-l/2-(turn)*(spacing)        
            r = r0 + offset         
            t = Trans(Trans.R0,xo, yo)
            self.cell.shapes(wg_layer).insert(arc_wg(r, w, 180., 270.).transformed(t))
            if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + (1/2 * pi * r0) * dbu
                
            # left lines
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint(-w/2, -yo+spacing)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(-w/2, yo)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(w/2, yo)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(w/2, -yo+spacing)))
            line = pya.Polygon(pts)
            t = Trans(Trans.R0,xo-r, 0)
            self.cell.shapes(wg_layer).insert(line.transformed(t))
            if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + abs(2 * yo - spacing) * dbu
                
            # top left corner
            xo=-r0-(turn)*(spacing)
            yo=l/2+(turn+1)*(spacing)        
            r = r0 + offset         
            t = Trans(Trans.R0,xo, yo)
            self.cell.shapes(wg_layer).insert(arc_wg(r, w, 90., 180.).transformed(t))
            if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + (1/2 * pi * r0) * dbu
                
            # top lines
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint(xo, -w/2)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(-xo+spacing,-w/2)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(-xo+spacing,w/2)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(xo,w/2)))
            line = pya.Polygon(pts)
            t = Trans(Trans.R0,0, yo+r)
            self.cell.shapes(wg_layer).insert(line.transformed(t))   
            if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + abs(2 * xo - spacing) * dbu
                
        # Bring the ends together 
        if self.spiral_ports:
            turn = self.nsp-1
            # top right corner
            xo=r0+(turn)*(spacing)
            yo=l/2+(turn)*(spacing)        
            r = r0 + offset         
            t = Trans(Trans.R0,xo, yo)
            self.cell.shapes(wg_layer).insert(arc_wg(r, w, 0., 90.).transformed(t))
            if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + (1/2 * pi * r0) * dbu
                
            # right lines
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint(-w/2, -yo-spacing)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(-w/2, yo)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(w/2, yo)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(w/2, -yo-spacing)))
            line = pya.Polygon(pts)
            t = Trans(Trans.R0,xo+r, 0)
            self.cell.shapes(wg_layer).insert(line.transformed(t))
            if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + abs(2 * yo + spacing) * dbu
                
            # bottom right corner
            xo=r0+(turn)*(spacing)
            yo=-l/2-(turn+1)*(spacing)        
            r = r0 + offset         
            t = Trans(Trans.R0,xo, yo)
            self.cell.shapes(wg_layer).insert(arc_wg(r, w, 270., 360.).transformed(t))
            if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + (1/2 * pi * r0) * dbu
                
            # bottom lines
            pts = []
            pts.append(pya.Point.from_dpoint(pya.DPoint(xo, -w/2)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(-xo-spacing,-w/2)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(-xo-spacing,w/2)))
            pts.append(pya.Point.from_dpoint(pya.DPoint(xo,w/2)))
            line = pya.Polygon(pts)
            t = Trans(Trans.R0,0, yo-r)
            self.cell.shapes(wg_layer).insert(line.transformed(t))          
            if self.layout.layer(TECHNOLOGY['Waveguide']) == wg_layer:
                spiral_length = spiral_length + abs(2 * xo + spacing) * dbu

    self.spiral_length = spiral_length
    # Pins on the waveguide:
    pin_length = 0.02/dbu
    
    x=-r0-(self.nsp-1)*(spacing)
    y=-l/2-(self.nsp-1)*(spacing)-r0 
    w = self.wg_width / dbu
    t = Trans(Trans.R0, x,y)
    pin = Path([Point(pin_length/2,0), Point(-pin_length/2,0)], w)
    pin_t = pin.transformed(t)
    shapes(LayerPinRecN).insert(pin_t)
    text = Text ("pin2", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    if self.spiral_ports:
        x=-r0-(self.nsp)*(spacing)
        y=-l/2-(self.nsp)*(spacing)-r0 
        pin = Path([Point(pin_length/2,0), Point(-pin_length/2,0)], w)
    else:
        x=r0+(self.nsp-1)*(spacing)
        y=l/2+(self.nsp-1)*(spacing)+r0 
        pin = Path([Point(-pin_length/2,0), Point(pin_length/2,0)], w)
    t = Trans(Trans.R0, x,y)
    pin_t = pin.transformed(t)
    shapes(LayerPinRecN).insert(pin_t)
    text = Text ("pin1", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    # Compact model information
    t = Trans(Trans.R0, 0, 0)
    text = Text ('Lumerical_INTERCONNECT_library='+self.CML, t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = 0.1/dbu
    t = Trans(Trans.R0, 0, self.wg_width*2/dbu)
    text = Text ('Component='+self.model, t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = 0.1/dbu
    t = Trans(Trans.R0, 0, -self.wg_width*2/dbu)
    text = Text \
      ('Spice_param:wg_length=%.3fu wg_width=%.3fu min_radius=%.3fu wg_spacing=%.3fu' %\
      (spiral_length, self.wg_width, self.r0, self.s), t )
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = 0.1/dbu
    
    text_x = 2*r0+(self.nsp)*spacing
    t = Trans(Trans.R0, -abs(text_x), 0)
    text = Text ('Length=%.3fu' % spiral_length, t)
    shape = shapes(LayerTextN).insert(text)
    shape.text_size = abs(text_x)/8


    # Create the device recognition layer -- make it 1 spacing away from the waveguides.
    pts = []
    pts.append(pya.Point.from_dpoint(pya.DPoint(2*r0+(self.nsp+1)*spacing, 1/2*l+r0+(self.nsp+1)*spacing)))
    pts.append(pya.Point.from_dpoint(pya.DPoint(-2*r0-(self.nsp+1)*spacing, 1/2*l+r0+(self.nsp+1)*spacing)))
    pts.append(pya.Point.from_dpoint(pya.DPoint(-2*r0-(self.nsp+1)*spacing, -1/2*l-r0-(self.nsp+1)*spacing)))
    pts.append(pya.Point.from_dpoint(pya.DPoint(2*r0+(self.nsp+1)*spacing, -1/2*l-r0-(self.nsp+1)*spacing)))    
    shapes(LayerDevRecN).insert(Polygon(pts))
 
    print("ebeam_pcell_waveguide_spiral_square done.")