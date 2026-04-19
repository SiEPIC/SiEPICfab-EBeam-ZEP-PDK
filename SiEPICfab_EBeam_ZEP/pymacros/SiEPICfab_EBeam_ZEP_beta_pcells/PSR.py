from . import *
from pya import *
from SiEPIC.utils.layout import layout_waveguide2, layout_taper, layout_waveguide_sbend
import pya
from SiEPIC.utils import get_technology_by_name

class PSR(pya.PCellDeclarationHelper):
    """
    The PCell declaration for the strip waveguide taper.
    """
    def __init__(self):
        # Important: initialize the super class
        super(PSR, self).__init__()
        TECHNOLOGY = get_technology_by_name('SiEPICfab_EBeam_ZEP')

        # declare layer params
        self.param("layer", self.TypeLayer, "Si Layer", default = TECHNOLOGY['Si_core'])
        self.param("clad", self.TypeLayer, "Cladding Layer", default = TECHNOLOGY['Si_clad'])
        self.param("clad_width", self.TypeDouble, "Cladding Width", default = 2)
        self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'])
        self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'])
        
        # declare port widths
        self.param("w_thru", self.TypeDouble, "Thru Port Width (um)", default = 0.55)
        self.param("w_cross", self.TypeDouble, "Cross Port Width (um)", default = 0.55)
        
        # declare taper params
        self.param("w_tin", self.TypeDouble, "Taper: Width - Waveguide Input (um)", default = 0.45)
        self.param("w_twmid", self.TypeDouble, "Taper: Width - Waveguide Mid (um)", default = 0.55)
        self.param("w_tc", self.TypeDouble, "Taper: Width - Waveguide Output (um)", default = 0.85)
        self.param("w_tsmid", self.TypeDouble, "Taper: Width - Slab Mid (um)", default = 1.55)

        self.param("la", self.TypeDouble, "Taper: Length - Input to Mid (um)", default = 35.0)
        self.param("lb", self.TypeDouble, "Taper: Length - Mid to Output (um)", default = 30.0)

        # declare coupler params
        self.param("w_out", self.TypeDouble, "Coupler: Output Width (um)", default = 0.45)
        self.param("lc", self.TypeDouble, "Coupler: Length (um)", default = 100.0)
        self.param("g", self.TypeDouble, "Coupler: Gap (um)", default = 0.13)
        
        # declare SWG params
        self.param("w_swg_in", self.TypeDouble, "SWG: Input Width (um)", default = 0.65)
        self.param("w_swg_mid", self.TypeDouble, "SWG: Output Width (um)", default = 0.55)
        self.param("l_swg_out", self.TypeDouble, "SWG: Output Taper Length (um)", default = 10.0)
        self.param("period", self.TypeDouble, "SWG: Period (um)", default = 0.2)
        self.param("ff", self.TypeDouble, "SWG: Fill Factor (um)", default = 0.6)

        # hidden parameters, can be used to query this component:
        self.param("p1", self.TypeShape, "DPoint location of pin1", default = Point(-10000, 0), hidden = True, readonly = True)
        self.param("p2", self.TypeShape, "DPoint location of pin2", default = Point(0, 10000), hidden = True, readonly = True)
        self.param("p3", self.TypeShape, "DPoint location of pin3", default = Point(0, -10000), hidden = True, readonly = True)
    
    def coerce_parameters_impl(self):
        n_periods = int(self.lc/self.period)
        self.lc = self.period*n_periods
        min_grating_s = float(self.period*(1-self.ff))
        min_grating_f = float(self.period*self.ff)
      
    def display_text_impl(self):
        # Provide a descriptive text for the cell
        psr_params = ('%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f' % 
                      (self.w_tin,self.w_twmid,self.w_tsmid, self.w_tc,
                       self.la, self.lb, self.w_out, self.lc, self.g,
                       self.w_swg_in, self.w_swg_mid, self.l_swg_out,
                       self.period, self.ff) )
        return "PSR(" + psr_params + ")"

    def can_create_from_shape(self):
        return False
    
    def produce_impl(self):
        """
        coerce parameters (make consistent)
        """
        
        # Import constants for creating pins
        from SiEPIC._globals import PIN_LENGTH as pin_length
        from SiEPIC.extend import to_itype
        import math
        from pya import DPolygon
    
        # cell: layout cell to place the layout
        # LayerSiN: which layer to use
        # w: waveguide width
        # length units in dbu
    
        # fetch the parameters
        dbu = self.layout.dbu
        ly = self.layout
        shapes = self.cell.shapes
        clad_width = self.clad_width/dbu
        
        LayerSi = ly.layer(self.layer)
        LayerClad = ly.layer(self.clad)
        LayerPinRecN = ly.layer(self.pinrec)
        LayerDevRecN = ly.layer(self.devrec)
        
        # Top PSR Wdiths
        w1 = int(round(self.w_tin/dbu))
        w2 = int(round(self.w_twmid/dbu))
        
        w7 = int(round(self.w_tsmid/dbu))
        
        w3 = int(round(self.w_tc/dbu))
        w4 = int(round(self.w_out/dbu))
        
        # SWG Widths
        w5 = int(round(self.w_swg_in/dbu))
        w6 = int(round(self.w_swg_mid/dbu))
        
        # Thru and Cross Port Widths
        w8 = int(round(self.w_thru/dbu))
        w9 = int(round(self.w_cross/dbu))
        
        # S-Bend params
        radius_um, adiab, bezier = 5, 1, 0.2 # Bezier parameters
        
        la = int(round(self.la/dbu))
        lb = int(round(self.lb/dbu))
        
        n_periods = int(self.lc/self.period)
        self.lc = self.period*n_periods
        lc = int(round(self.lc/dbu))
        ld = int(round(self.l_swg_out/dbu))
        
        g = int(round(self.g/dbu))
        period = int(round(self.period/dbu))
        ff = int(round(self.ff/dbu))
        
        # Constants
        io_wg_length = int(round(10.0/dbu))
        slab_overlap = int(round(8.0/dbu))
        buffer_length = 4.0
        buffer_wg_length = int(round(buffer_length/dbu))
        hi_res_height = int(round(0.1/dbu))
        
        ############# PSR TOP #############
        # Create a list of coordinates to draw for the top waveguide portion of PSR
        coords_PSR_top_wg = [[-io_wg_length,w1/2] ,[0,w1/2], [la, w2/2], [la+lb, w3/2], [la+lb+buffer_wg_length, w3/2],  [la+lb+buffer_wg_length+lc, w4/2], 
                          [la+lb+buffer_wg_length+lc, -w4/2], [la+lb+buffer_wg_length, -w3/2], [la+lb, -w3/2], [la, -w2/2], [0, -w1/2], [-io_wg_length,-w1/2]]
        
        # Draw the top waveguide portion of the PSR
        pts = []
        for xy in coords_PSR_top_wg:
            pts.append(Point(xy[0], xy[1]))
        self.cell.shapes(LayerSi).insert(Polygon(pts))
        
        # Add s-bend to top right output waveguide
        x,y=la+lb+lc+buffer_wg_length,0
        #layout_waveguide_sbend(cell, Layer_Si220, pya.Trans(Trans.R0, x,y), w=W5, r=15/dbu, h=4/dbu, length=15/dbu) # s-bend
        L=radius_um/dbu
        pts = [Point(x,y), Point(x+L,y), Point(x+L,y+2*L),Point(x+2*L,y+2*L)]
        TECHNOLOGY = get_technology_by_name('SiEPICfab_EBeam_ZEP')
        waveguide = layout_waveguide2(TECHNOLOGY, ly, self.cell, ['Si_core'], [w4*dbu], [0], pts, radius_um, adiab, bezier)
    
        # s-bend waveguide cladding
        clad_box1 = Box(Point(x,y-clad_width), Point(x+2*L,y+2*L+w4/2+clad_width))
        shapes(LayerClad).insert(Polygon(clad_box1))
        x,y=x+2*L,y+2*L
        
        # taper 
        L = io_wg_length+ld-2*L
        layout_taper(self.cell, LayerSi, pya.Trans(Trans.R0, x,y), w1=w4, w2=w8, length=L) 
        x1,y1=x+L,y

        # taper waveguide cladding
        pts = [Point(x,y-w4/2-clad_width), Point(x,y+w4/2+clad_width), Point(x+L,y+w8/2+clad_width), Point(x+L,y-w8/2-clad_width)]
        shapes(LayerClad).insert(Polygon(pts))
        
        # Set bounds for DevRec
        top_bound = max([y1 - w8/2 + w4/2, y1 + w8/2])
        right_bound = x1
        
        # Pin on the left side:
        p1 = [Point(-io_wg_length-pin_length/2,0), Point(-io_wg_length+pin_length/2,0)]
        p1c = Point(-io_wg_length,0)
        self.set_p1 = p1c
        self.p1 = p1c
        pin = Path(p1, w1)
        self.cell.shapes(LayerPinRecN).insert(pin)
        t = Trans(Trans.R0, -io_wg_length, 0)
        text = Text ("pin1", t)
        shape = self.cell.shapes(LayerPinRecN).insert(text)
        shape.text_size = 0.4/dbu
    
        # Pin on the top right side:
        p2 = [Point(x1-pin_length/2, y1), Point(x1+pin_length/2, y1)]
        p2c = Point(x1, y1)
        self.set_p2 = p2c
        self.p2 = p2c
        pin = Path(p2, w8)
        self.cell.shapes(LayerPinRecN).insert(pin)
        t = Trans(Trans.R0, x1, y1)
        text = Text ("pin2", t)
        shape = self.cell.shapes(LayerPinRecN).insert(text)
        shape.text_size = 0.4/dbu
        shape.text_halign = 2
        
        
        ############# PSR BOTTOM #############
        slope_coup = (self.w_tc/2 - self.w_out/2)/self.lc
        slope_swg = (self.w_swg_mid - self.w_swg_in)/self.lc
        
        # Create left SWG in coupling section
        pts = []
        for i in range(0, n_periods):
            x1 = self.la + self.lb + buffer_length + i*self.period
            y2 = -self.w_tc/2 - self.g + i*self.period*slope_coup 
            y1 = y2 - self.w_swg_in - i*self.period*slope_swg
            
            y_top_mid1 = y2 - (y2 - y1)/2 + self.w_swg_in/2
            pts.append(Point(int(round(x1/dbu)),int(round(y_top_mid1/dbu))))
            pts.append(Point(int(round(x1/dbu)),int(round(y2/dbu))))
            
            x2 = self.la + self.lb + buffer_length + (i*self.period) + self.period*self.ff
            y3 = -self.w_tc/2 - self.g + self.period*(i + self.ff)*slope_coup 
            y4 = y3 - self.w_swg_in - self.period*(i + self.ff)*slope_swg
            
            y_top_mid2 = y3 - (y3 - y4)/2 + self.w_swg_in/2
            pts.append(Point(int(round(x2/dbu)),int(round(y3/dbu))))
            pts.append(Point(int(round(x2/dbu)),int(round(y_top_mid2/dbu))))
        
        # Create SWG to output waveguide
        slope_swg_out = (self.w_swg_mid/2 - self.w_cross/2) / self.l_swg_out
        slope_wg_out = (self.w_cross/2 - self.w_swg_in/2) / self.l_swg_out
        i = 0
        while i < int(round(self.l_swg_out / self.period)):
            x = self.la + self.lb + buffer_length + self.lc + (i*self.period)
            y1 = -self.w_out/2 - self.g - self.w_swg_mid/2 + self.w_swg_in/2 + ((i*self.period) + self.period*(1-self.ff))*slope_wg_out
            y2 = -self.w_out/2 - self.g - ((i*self.period) + self.period*(1-self.ff))*slope_swg_out
            pts.append(Point(int(round(x/dbu)),int(round(y1/dbu))))
            pts.append(Point(int(round(x/dbu)),int(round(y2/dbu))))
            
            x = self.la + self.lb + buffer_length + self.lc + (i+self.ff)*self.period
            y1 = -self.w_out/2 - self.g - (i+1)*self.period*slope_swg_out
            y2 = -self.w_out/2 - self.g - self.w_swg_mid/2 + self.w_swg_in/2 + (i+1)*self.period*slope_wg_out
            pts.append(Point(int(round(x/dbu)),int(round(y1/dbu))))
            pts.append(Point(int(round(x/dbu)),int(round(y2/dbu))))
            i = i+1
            
        # Add output waveguide
        pts.append(Point(right_bound,int(round(y2/dbu))))
        pts.append(Point(right_bound,int(round(y2/dbu))-w9))
        
        # Pin on the bottom right side:
        p3 = [Point(right_bound-pin_length/2, int(round(y2/dbu))-w9/2), Point(right_bound+pin_length/2,int(round(y2/dbu))-w9/2)]
        p3c = Point(right_bound, int(round(y2/dbu))-w9/2)
        self.set_p3 = p3c
        self.p3 = p3c
        pin = Path(p3, w9)
        self.cell.shapes(LayerPinRecN).insert(pin)
        t = Trans(Trans.R0, right_bound, int(round(y2/dbu))-w9/2)
        text = Text ("pin3", t)
        shape = self.cell.shapes(LayerPinRecN).insert(text)
        shape.text_size = 0.4/dbu
        shape.text_halign = 2
        
        # Create bottom pts of the SWG waveguide
        swg_bot_pts = []
        for i in range(0, n_periods):
            
            x1 = self.la + self.lb + buffer_length + i*self.period
            y2 = -self.w_tc/2 - self.g + i*self.period*slope_coup 
            y1 = y2 - self.w_swg_in - i*self.period*slope_swg
            
            y_bot_mid1 = y2 - (y2 - y1)/2 - self.w_swg_in/2
            swg_bot_pts.append(Point(int(round(x1/dbu)),int(round(y_bot_mid1/dbu))))
            swg_bot_pts.append(Point(int(round(x1/dbu)),int(round(y1/dbu))))
            
            x2 = self.la + self.lb + buffer_length + (i*self.period) + self.period*self.ff
            y3 = -self.w_tc/2 - self.g + self.period*(i + self.ff)*slope_coup 
            y4 = y3 - self.w_swg_in - self.period*(i + self.ff)*slope_swg
            
            y_bot_mid2 = y3 - (y3 - y4)/2 - self.w_swg_in/2
            swg_bot_pts.append(Point(int(round(x2/dbu)),int(round(y4/dbu))))
            swg_bot_pts.append(Point(int(round(x2/dbu)),int(round(y_bot_mid2/dbu))))
        
        i = 0
        while i < int(round(self.l_swg_out / self.period)):
            x = self.la + self.lb + buffer_length + self.lc + (i*self.period)
            y1 = -self.w_out/2 - self.g - self.w_swg_mid/2 - self.w_swg_in/2 - ((i*self.period) + self.period*(1-self.ff))*slope_wg_out
            y2 = -self.w_out/2 - self.g - self.w_swg_mid + ((i*self.period) + self.period*(1-self.ff))*slope_swg_out
            swg_bot_pts.append(Point(int(round(x/dbu)),int(round(y1/dbu))))
            swg_bot_pts.append(Point(int(round(x/dbu)),int(round(y2/dbu))))
            
            x = self.la + self.lb + buffer_length + self.lc + (i+self.ff)*self.period
            y1 = -self.w_out/2 - self.g - self.w_swg_mid + (i+1)*self.period*slope_swg_out
            y2 = -self.w_out/2 - self.g - self.w_swg_mid/2 - self.w_swg_in/2 - (i+1)*self.period*slope_wg_out
            swg_bot_pts.append(Point(int(round(x/dbu)),int(round(y1/dbu))))
            swg_bot_pts.append(Point(int(round(x/dbu)),int(round(y2/dbu))))
            i = i+1
        
        swg_bot_pts.reverse()
        for pt in swg_bot_pts:
            pts.append(pt)
        self.cell.shapes(LayerSi).insert(Polygon(pts))
        
        # Bounds for DevRec
        bottom_bound = min([pt.y for pt in swg_bot_pts])
        left_bound = -io_wg_length
        
        print("*********")
        print(bottom_bound)
        print(left_bound)
        
        # Create the device recognition layer        
        devrec_box = Box(Point(left_bound, bottom_bound-clad_width), Point(right_bound, top_bound+clad_width))
        self.cell.shapes(LayerDevRecN).insert(devrec_box)

        # waveguide cladding
        clad_box = Box(Point(left_bound, bottom_bound-clad_width), Point(right_bound, y1+w4/2+clad_width))
        shapes(LayerClad).insert(clad_box)
        
        psr_params = ('%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f-%.3f' % 
                      (self.w_tin,self.w_twmid,self.w_tsmid, self.w_tc,
                       self.la, self.lb, self.w_out, self.lc, self.g,
                       self.w_swg_in, self.w_swg_mid, self.l_swg_out,
                       self.period, self.ff) )
        
        return "PSR(" + psr_params + ")"