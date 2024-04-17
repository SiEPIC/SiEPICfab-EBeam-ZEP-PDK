from . import *
from pya import *

class ebeam_taper_modal(pya.PCellDeclarationHelper):
  """
  The PCell declaration for the strip waveguide taper.
  """

  def __init__(self):

    # Important: initialize the super class
    super(ebeam_taper_modal, self).__init__()
    TECHNOLOGY = get_technology_by_name('SiEPICfab_EBeam_ZEP')

    # declare the parameters
    self.param("silayer", self.TypeLayer, "Si Layer", default = TECHNOLOGY['Si_core'])
    self.param("clad_layer", self.TypeLayer, "Clad Layer", default = TECHNOLOGY['Si_clad'])
    self.param("io_length", self.TypeDouble, "IO Length", default = 1)
    self.param("wg_width1", self.TypeDouble, "Waveguide Width1", default = 0.5)
    self.param("wg_width2", self.TypeDouble, "Waveguide Width2", default = 3)
    self.param("wg_length", self.TypeDouble, "Waveguide Length", default = 20)
    self.param("taper_type", self.TypeString, "Taper Type (lin, par, ell, cpar, cell, s, ctl)", default = "s")
    self.param("ctl_file", self.TypeString, "Segments Files (For Custom Taper)", default = "")
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'])
    # hidden parameters, can be used to query this component:
    self.param("p1", self.TypeShape, "DPoint location of pin1", default = Point(-10000, 0), hidden = True, readonly = True)
    self.param("p2", self.TypeShape, "DPoint location of pin2", default = Point(0, 10000), hidden = True, readonly = True)
    

  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "ebeam_taper(R=" + ('%.3f-%.3f-%.3f' % (self.wg_width1,self.wg_width2,self.wg_length) ) + ")"

  def can_create_from_shape_impl(self):
    return False


  def produce(self, layout, layers, parameters, cell):
    """
    coerce parameters (make consistent)
    """
    import numpy as np
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
    LayerCladN = ly.layer(self.clad_layer)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
    
    in_width = int(round(self.wg_width1/dbu))
    out_width = int(round(self.wg_width2/dbu))
    length = int(round(self.wg_length/dbu))
    taper_type = self.taper_type
    io_length = int(round(self.io_length/dbu))
    if io_length > 0:
        include_output_wg = True
    else:
        include_output_wg = False
    
    num_pts = 1000
    x = np.linspace(0, length, num_pts+1)
    xr = np.flip(x)
    if taper_type == "lin":
        if include_output_wg:
            pts = [[-io_length, in_width/2], [0, in_width/2], [length, out_width/2], [length+io_length, out_width/2],
                   [length+io_length, -out_width/2], [length, -out_width/2],  [0, -in_width/2], [-io_length, -in_width/2]]
        else:
            pts = [[-io_length, in_width/2], [0, in_width/2], [length, out_width/2], 
                   [length, -out_width/2],  [0, -in_width/2], [-io_length, -in_width/2]]
    elif taper_type == "s":
        x = np.linspace(0, length, num_pts+1)
        xr = np.flip(x)
        if include_output_wg:
            y = in_width/2 + (out_width/2 - in_width/2)*np.sin(np.pi/2*x/length)**2
            yr = -np.flip(y)
            
            pts = [[-io_length, in_width/2], [0, in_width/2]]
            for i in range(0, len(x)):
                pts.append([x[i], y[i]])
            
            # Append output wg
            pts.append([x[-1]+io_length, y[-1]])
            pts.append([xr[0]+io_length, yr[0]])
            
            for i in range(0, len(xr)):
                pts.append([xr[i], yr[i]])
                
            # Append input wg
            pts.append([0, -in_width/2])
            pts.append([-io_length, -in_width/2])
        else:
            y = in_width/2 + (out_width/2 - in_width/2)*np.sin(np.pi/2*x/length)**2
            yr = -np.flip(y)
            
            pts = [[-io_length, in_width/2], [0, in_width/2]]
            for i in range(0, len(x)):
                pts.append([x[i], y[i]])
                
            for i in range(0, len(xr)):
                pts.append([xr[i], yr[i]])
                
            # Append input wg
            pts.append([0, -in_width/2])
            pts.append([-io_length, -in_width/2])
    elif taper_type == "ss":
        if include_output_wg:
            s = ratio_stretch_terms*x + (1-ratio_stretch_terms)*(x/length)**stretch_exponent*length
            y = in_width/2 + (out_width/2 - in_width/2)*np.sin(np.pi/2*s/length)**2
            yr = -np.flip(y)
            
            pts = [[-io_length, in_width/2], [0, in_width/2]]
            for i in range(0, len(x)):
                pts.append([x[i], y[i]])
            
            # Append output wg
            pts.append([x[-1]+io_length, y[-1]])
            pts.append([xr[0]+io_length, yr[0]])    
            
            for i in range(0, len(xr)):
                pts.append([xr[i], yr[i]])
                
            # Append input wg
            pts.append([0, -in_width/2])
            pts.append([-io_length, -in_width/2])
        else:
            s = ratio_stretch_terms*x + (1-ratio_stretch_terms)*(x/length)**stretch_exponent*length
            y = in_width/2 + (out_width/2 - in_width/2)*np.sin(np.pi/2*s/length)**2
            yr = -np.flip(y)
            
            pts = [[-io_length, in_width/2], [0, in_width/2]]
            for i in range(0, len(x)):
                pts.append([x[i], y[i]])
                
            for i in range(0, len(xr)):
                pts.append([xr[i], yr[i]])
                
            # Append input wg
            pts.append([0, -in_width/2])
            pts.append([-io_length, -in_width/2])
    elif taper_type == "par":
        if include_output_wg:
            y = in_width/2 + (out_width - in_width)/2*(x/length)**0.5
            yr = -np.flip(y)
            
            pts = [[-io_length, in_width/2], [0, in_width/2]]
            for i in range(0, len(x)):
                pts.append([x[i], y[i]])
            
            # Append output wg
            pts.append([x[-1]+io_length, y[-1]])
            pts.append([xr[0]+io_length, yr[0]])      
            
            for i in range(0, len(xr)):
                pts.append([xr[i], yr[i]])
                
            # Append input wg
            pts.append([0, -in_width/2])
            pts.append([-io_length, -in_width/2])
        else:
            y = in_width/2 + (out_width - in_width)/2*(x/length)**0.5
            yr = -np.flip(y)
            
            pts = [[-io_length, in_width/2], [0, in_width/2]]
            for i in range(0, len(x)):
                pts.append([x[i], y[i]])
                
            for i in range(0, len(xr)):
                pts.append([xr[i], yr[i]])
                
            # Append input wg
            pts.append([0, -in_width/2])
            pts.append([-io_length, -in_width/2])
    elif taper_type == "cpar":
        if include_output_wg:
            y = out_width/2 - (out_width - in_width)/2*(1-x/length)**0.5
            yr = -np.flip(y)
            
            pts = [[-io_length, in_width/2], [0, in_width/2]]
            for i in range(0, len(x)):
                pts.append([x[i], y[i]])
            
            # Append output wg
            pts.append([x[-1]+io_length, y[-1]])
            pts.append([xr[0]+io_length, yr[0]])      
            
            for i in range(0, len(xr)):
                pts.append([xr[i], yr[i]])
                
            # Append input wg
            pts.append([0, -in_width/2])
            pts.append([-io_length, -in_width/2])
        else:
            y = out_width/2 - (out_width - in_width)/2*(1-x/length)**0.5
            yr = -np.flip(y)
            
            pts = [[-io_length, in_width/2], [0, in_width/2]]
            for i in range(0, len(x)):
                pts.append([x[i], y[i]])
                
            for i in range(0, len(xr)):
                pts.append([xr[i], yr[i]])
                
            # Append input wg
            pts.append([0, -in_width/2])
            pts.append([-io_length, -in_width/2])
    elif taper_type == "ell":
        if include_output_wg:
            y = in_width/2 + (out_width - in_width)/2*(1-(1-x/length)**2)**0.5
            yr = -np.flip(y)
            
            pts = [[-io_length, in_width/2], [0, in_width/2]]
            for i in range(0, len(x)):
                pts.append([x[i], y[i]])
            
            # Append output wg
            pts.append([x[-1]+io_length, y[-1]])
            pts.append([xr[0]+io_length, yr[0]])    
            
            for i in range(0, len(xr)):
                pts.append([xr[i], yr[i]])
                
            # Append input wg
            pts.append([0, -in_width/2])
            pts.append([-io_length, -in_width/2])
        else:
            y = in_width/2 + (out_width - in_width)/2*(1-(1-x/length)**2)**0.5
            yr = -np.flip(y)
            
            pts = [[-io_length, in_width/2], [0, in_width/2]]
            for i in range(0, len(x)):
                pts.append([x[i], y[i]])
                
            for i in range(0, len(xr)):
                pts.append([xr[i], yr[i]])
                
            # Append input wg
            pts.append([0, -in_width/2])
            pts.append([-io_length, -in_width/2])
    elif taper_type == "cell":
        if include_output_wg:
            y = out_width/2 - (out_width - in_width)/2*(1-(x/length)**2)**0.5
            yr = -np.flip(y)
            
            pts = [[-io_length, in_width/2], [0, in_width/2]]
            for i in range(0, len(x)):
                pts.append([x[i], y[i]])
            
            # Append output wg
            pts.append([x[-1]+io_length, y[-1]])
            pts.append([xr[0]+io_length, yr[0]])      
            
            for i in range(0, len(xr)):
                pts.append([xr[i], yr[i]])
                
            # Append input wg
            pts.append([0, -in_width/2])
            pts.append([-io_length, -in_width/2])
        else:
            y = out_width/2 - (out_width - in_width)/2*(1-(x/length)**2)**0.5
            yr = -np.flip(y)
            
            pts = [[-io_length, in_width/2], [0, in_width/2]]
            for i in range(0, len(x)):
                pts.append([x[i], y[i]])
                
            for i in range(0, len(xr)):
                pts.append([xr[i], yr[i]])
                
            # Append input wg
            pts.append([0, -in_width/2])
            pts.append([-io_length, -in_width/2])
    elif taper_type == "ctl":
        segments = np.genfromtxt(self.ctl_file, delimiter=',')
        
        x = np.array([0])
        for i in range(0, len(segments)):
            x = np.append(x, sum(segments[0:i+1]))
        if x[-1] < 10:
            x = np.append(x, 10)    
            
        x = (x / 10000 * length) / dbu
        
        xr = np.flip(x)
        
        y = np.linspace(in_width/2, out_width/2, len(x))
        yr = -np.flip(y)
        
        # Extract points
        pts = [[-io_length, in_width/2], [0, in_width/2]]
        for i in range(0, len(x)):
            pts.append([x[i], y[i]])
        
        # Append output wg
        pts.append([x[-1]+io_length, y[-1]])
        pts.append([xr[0]+io_length, yr[0]])   
            
        for i in range(0, len(xr)):
            pts.append([xr[i], yr[i]])
            
        # Append input wg
        pts.append([0, -in_width/2])
        pts.append([-io_length, -in_width/2])
        

    pts = [Point(pt[0],pt[1]) for pt in pts]
    shapes(LayerSiN).insert(Polygon(pts))

    
    # Create the pins on the waveguides, as short paths:
    from SiEPIC._globals import PIN_LENGTH as pin_length
    
    # Pin on the left side:
    p1 = [Point(pin_length/2 -io_length,0), Point(-pin_length/2 -io_length,0)]
    p1c = Point(-io_length,0)
    self.set_p1 = p1c
    self.p1 = p1c
    pin = Path(p1, in_width)
    shapes(LayerPinRecN).insert(pin)
    t = Trans(Trans.R0, -io_length, 0)
    text = Text ("opt1", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    # Pin on the right side:
    p2 = [Point(length+io_length-pin_length/2,0), Point(length+io_length+pin_length/2,0)]
    p2c = Point(length+io_length, 0)
    self.set_p2 = p2c
    self.p2 = p2c
    pin = Path(p2, out_width)
    shapes(LayerPinRecN).insert(pin)
    t = Trans(Trans.R0, length+io_length, 0)
    text = Text ("opt2", t)
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu
    shape.text_halign = 2

    # Create the device recognition layer -- make it 1 * wg_width away from the waveguides.
    path = Path([Point(-io_length,0),Point(length+io_length,0)], max([out_width, in_width]) + int(round(2/dbu)))
    shapes(LayerDevRecN).insert(path.simple_polygon())
    shapes(LayerCladN).insert(path.simple_polygon())


    # Compact model information
    t = Trans(Trans.R0, in_width/10, 0)
    text = Text ("Lumerical_INTERCONNECT_library=None", t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = length/100
    t = Trans(Trans.R0, length/10, in_width/4)
    text = Text ('Component=ebeam_taper', t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = length/100
    t = Trans(Trans.R0, length/10, in_width/2)
    text = Text ('Spice_param:wg_width1=%.3fu wg_width2=%.3fu wg_length=%.3fu'% (self.wg_width1,self.wg_width2,self.wg_length), t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = length/100

    return "ebeam_taper(" + ('%.3f-%.3f-%.3f' % (self.wg_width1,self.wg_width2,self.wg_length) ) + ")"
