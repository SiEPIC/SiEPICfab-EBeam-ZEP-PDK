import pya
from pya import *

class strip_to_slot(pya.PCellDeclarationHelper):
    """
    The PCell declaration for the strip_to_slot.
    July 24, 2017 - Lukas Chrostowski
    March 17, 2021- Alexander Tofini
    June 13, 2022 - Jaspreet Jhoja
    based on https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-21-16-19029&id=259920
    """

    def __init__(self):       
        super(strip_to_slot, self).__init__()
        from SiEPIC.utils import get_technology_by_name
        TECHNOLOGY = get_technology_by_name('SiEPICfab_EBeam_ZEP')
        # declare the parameters
        self.param("silayer", self.TypeLayer, "Si Layer", default = TECHNOLOGY['Si_core'])
        self.param("clad", self.TypeLayer, "Cladding Layer", default = TECHNOLOGY['Si_clad'])
        self.param("r", self.TypeDouble, "Radius", default = 10)
        self.param("w", self.TypeDouble, "Waveguide Width", default = 0.5)
        self.param("rails", self.TypeDouble, "Rails", default=0.25) 
        self.param("slot", self.TypeDouble, "Slot", default=0.1)
        self.param("taper",self.TypeDouble,"Taper Length",default=10.0)   
        self.param("pinrec", self.TypeLayer, "PinRec Layer", default = TECHNOLOGY['PinRec'])
        self.param("devrec", self.TypeLayer, "DevRec Layer", default = TECHNOLOGY['DevRec'])
        self.param("textl", self.TypeLayer, "Text Layer", default = TECHNOLOGY['Text'])
    
    def display_text_impl(self):
        # Provide a descriptive text for the cell
        return "Strip_To_Slot(rails=" + ('%.3f' % self.rails) + ",slot=" + ('%g' % ( self.slot)) + ")"

    def can_create_from_shape_impl(self):
        return False

    def produce_impl(self):
        # This is the main part of the implementation: create the layout
     
        from math import pi, cos, sin
        from SiEPIC.utils import arc
        from SiEPIC.utils import arc_xy
        from SiEPIC.extend import to_itype
        from SiEPIC.utils import arc_wg_xy
        
        # fetch the parameters
        dbu = self.layout.dbu
        ly = self.layout
        cell = self.cell
        shapes = self.cell.shapes

        LayerSi = self.silayer
        LayerSiN = ly.layer(LayerSi)
        LayerCladN = ly.layer(self.clad)
        LayerPinRecN = ly.layer(self.pinrec)
        LayerDevRecN = ly.layer(self.devrec)

        # Use to_itype() to prevent rounding errors
        w = to_itype(self.w, dbu)
        r = to_itype(self.r, dbu)
        slot = to_itype(self.slot, dbu)
        rails = to_itype(self.rails, dbu)
        taper = to_itype(self.taper,dbu)
        # draw the quarter-circle
        x = 0
        y = r + rails/2 + w + slot
        
        dilation = 2/dbu

        t = Trans(Trans.R0, x, y)
        #self.cell.shapes(LayerSiN).insert(Path(arc(r, 270, 360), rails).transformed(t).simple_polygon())
        arc_circle = arc_wg_xy(x,y,r,rails,270,360)
        shapes(LayerSiN).insert(arc_circle)
        
        arc_circle = arc_wg_xy(x,y,r,rails,270,360)
        arc_circle.size(dilation)
        #shapes(LayerCladN).insert(arc_circle)
            
        pts = []     
        pts.append(Point.from_dpoint(DPoint(0, w)))
        pts.append(Point.from_dpoint(DPoint(0, 0)))
        pts.append(Point.from_dpoint(DPoint(-taper, w-rails )))
        pts.append(Point.from_dpoint(DPoint(-taper,w)))
        polygon = Polygon(pts)
        shapes(LayerSiN).insert(polygon)
        
        polygon = Polygon(pts)
        polygon.size(dilation)
        #shapes(LayerCladN).insert(polygon)
        clad_shape = pya.Region(arc_circle) + pya.Region(polygon)

        
        # Create the top left 1/2 waveguide
        wg1 = Box(-taper, w+slot, 0, w+rails+slot)
        shapes(LayerSiN).insert(wg1)
        
        wg1 = Box(-taper, w+slot, 0, w+rails+slot)
        wg1_l = wg1.enlarged(dilation, dilation)
        clad_shape = clad_shape + pya.Region(wg1_l)
        #shapes(LayerCladN).insert(wg1_l)

        from math import pi, cos, sin
        from SiEPIC.utils import arc_wg, arc_wg_xy
        from SiEPIC._globals import PIN_LENGTH as pin_length
        

        # Create the waveguide
        wg1 = Box(0, 0, r+w+dilation , w )
        shapes(LayerSiN).insert(wg1)
        
        wg1 = Box(0, 0, r+w+dilation , w )
        wg1_l = wg1.enlarged(0, dilation)
        #shapes(LayerCladN).insert(wg1_l)
        clad_shape = clad_shape + pya.Region(wg1_l)
        
        # Pin on the slot waveguide side:
        shapes(LayerPinRecN).insert(pya.Path([pya.Point(-taper+0.05/dbu, w+slot/2),
                                              pya.Point(-taper-0.05/dbu , w+slot/2)],2*rails+slot))
        shapes(LayerPinRecN).insert(pya.Text("opt1", pya.Trans(pya.Trans.R0, -taper, w))).text_size = 0.5 / dbu
        
        # Pin on the bus waveguide side:
        shapes(LayerPinRecN).insert(pya.Path([pya.Point(r+w+dilation-0.05/dbu, w/2),
                                              pya.Point(r+w+dilation+0.05/dbu , w/2)],w))
        shapes(LayerPinRecN).insert(pya.Text("opt2", pya.Trans(pya.Trans.R0, r+w+dilation, w/2))).text_size = 0.5 / dbu
        
        # Create the device recognition layer -- make it 1 * wg_width away from the waveguides.
        dev = Box(-taper, -w / 2 - w - dilation, r  + w+dilation , y+dilation)
        devrec_region = pya.Region(dev)
        
        clad_shape.merge()
        
        clad_shape = devrec_region & clad_shape
        
        shapes(LayerCladN).insert(clad_shape)
        
        shapes(LayerDevRecN).insert(dev)

        
