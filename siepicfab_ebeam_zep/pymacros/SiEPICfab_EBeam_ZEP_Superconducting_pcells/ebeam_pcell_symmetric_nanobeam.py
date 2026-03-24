# from . import *
import pya
from pya import *
import math


class ebeam_pcell_symmetric_nanobeam(pya.PCellDeclarationHelper):
    """
    Input: length, width
    """

    def __init__(self):
        super(ebeam_pcell_symmetric_nanobeam, self).__init__()
        from SiEPIC.utils import get_technology_by_name, load_Waveguides_by_Tech
        self.technology_name = 'SiEPICfab_EBeam_ZEP'
        TECHNOLOGY = get_technology_by_name(self.technology_name)
        self.TECHNOLOGY = TECHNOLOGY

        load_Waveguides_by_Tech(self.technology_name)

        self.param("w", self.TypeDouble, "Waveguide width (microns)", default=0.5)
        self.param("s", self.TypeDouble, "Cavity length (microns)", default=5)
        self.param("wg_l", self.TypeDouble, "Straight Waveguide length (microns)", default=0)

        self.param("n2", self.TypeInt, "Number of max radii holes", default=1)
        self.param("n1", self.TypeInt, "Number of tapered holes ", default=3)
        self.param("r_min", self.TypeDouble, "minimum radius", default=50)
        self.param("r_max_f", self.TypeDouble, "maximum radius on front reflector", default=70)

        self.param("enable_pos", self.TypeInt, "Enable positive side reflectors (1=True, 0=False)", default=1)
        self.param("enable_neg", self.TypeInt, "Enable negative side reflectors (1=True, 0=False)", default=1)
        self.param("taper_up", self.TypeInt, "Enable hole tapering up (1=True, 0=False)", default=0)

        self.param("pitch_scale", self.TypeDouble, "linear pitch scale (the m in y=mx+b) (unitless)", default=1.22)
        self.param("pitch_offset", self.TypeDouble, "linear pitch offset (the b in y=mx+b) (in nm)", default=308)

        self.param("n_vertices", self.TypeInt, "Vertices of a hole", default=32)
        self.param("layer", self.TypeLayer, "Layer - Waveguide", default=TECHNOLOGY['Si_core'])
        self.param("cladlayer", self.TypeLayer, "Cladding Layer", default=TECHNOLOGY['Si_clad'])
        self.param("pinrec", self.TypeLayer, "PinRec Layer", default=TECHNOLOGY['PinRec'])
        self.param("devrec", self.TypeLayer, "DevRec Layer", default=TECHNOLOGY['DevRec'])
        self.param("etch", self.TypeLayer, "oxide etch layer", default=TECHNOLOGY['Si_etch_highres'])
        self.param("extra_Si", self.TypeLayer, "Extra Si Layer", default=TECHNOLOGY['Si_etch_highres_nobias'])
        self.param("truncation_ext", self.TypeDouble,"Extra waveguide length (microns) for PreFab truncation handling", default=0.0)


    def display_text_impl(self):
        return "nanobeam_cavity_symmetric_%.2f_%.2f" % (self.w, self.s)

    def coerce_parameters_impl(self):
        pass

    def can_create_from_shape(self, layout, shape, layer):
        return False

    def produce_impl(self):
        import numpy as np
        import scipy as sp
        import math
        from scipy import interpolate
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
        s = self.s / dbu
        w = self.w / dbu
        n1 = self.n1
        n2 = self.n2
        r_min = self.r_min
        r_max_f = self.r_max_f
        n_vertices = self.n_vertices
        wg_l = self.wg_l / dbu
        truncation_ext = self.truncation_ext / dbu
        enable_pos = bool(self.enable_pos)
        enable_neg = bool(self.enable_neg)
        enable_taper_up = bool(self.taper_up)
        pitch_scale = self.pitch_scale  # convert to dbu
        pitch_offset = self.pitch_offset


        # function to generate points to create a circle
        def circle(x, y, r):
            npts = n_vertices
            theta = 2 * math.pi / npts  # increment, in radians
            pts = []
            for i in range(0, npts):
                pts.append(Point.from_dpoint(DPoint((x + r * math.cos(i * theta)) / 1, (y + r * math.sin(i * theta)) / 1)))
            return pts


                
    
        # raster through all holes with shifts and waveguide
        
        r_list_taper_up = np.linspace(r_min, r_max_f, n1+1)[:-1]
        r_list_taper_down = r_list_taper_up[::-1]
        r_list_plateau = np.full(n2, r_max_f)

        if enable_taper_up:
            r = np.concatenate([r_list_taper_up, r_list_plateau, r_list_taper_down])
        else:
            r = np.concatenate([r_list_taper_up, r_list_plateau])

        x_pos = []
        r_pos = []
        if enable_pos:
            x_pos = [s / 2]
            for i in range(1, len(r)):
                r_avg = 0.5 * (r[i - 1] + r[i])
                x_pos.append(x_pos[i - 1] + pitch_scale * r_avg + pitch_offset)
            r_pos = r

        x_neg = []
        r_neg = []
        if enable_neg:
            if enable_pos:
                r_mirror = r[::-1]
                x_neg = [-x for x in reversed(x_pos)]
                r_neg = r_mirror
            else:
                r_mirror = r[::-1]
                x_neg = [-s / 2]
                for i in range(1, len(r_mirror)):
                    r_avg = 0.5 * (r_mirror[i - 1] + r_mirror[i])
                    x_neg.append(x_neg[i - 1] - (pitch_scale * r_avg + pitch_offset))
                r_neg = r_mirror

        x_all = x_neg + x_pos
        r_all = list(r_neg) + list(r_pos)

        hole = Region()
        for i in range(len(r_all)):
            hole_poly = Polygon(circle(0, 0, r_all[i]))
            hole.insert(hole_poly.transformed(Trans(Trans.R0, x_all[i], 0)))
        self.cell.shapes(LayerHighResHoles).insert(hole)

        beam_l = max(abs(x_all[0]) if x_all else 0, abs(x_all[-1]) if x_all else 0) + wg_l



        Si_slab = Region()
        # Si_slab.insert(Box(-beam_l, -w / 2, -s/2, w / 2))
        
        # Si_slab.insert(Box(s/2, -w / 2, beam_l, w / 2))
        # Si_slab.insert(Box(-0.05/dbu, 1/dbu, 0.05/dbu,3/dbu))
        # Si_slab.insert(Box(-0.05/dbu, -1/dbu, 0.05/dbu,-3/dbu))
        Si_slab.insert(Box(0, -w / 2, beam_l, w / 2))
        Si_slab.insert(Box(-beam_l, -w / 2, 0, w / 2))

        self.cell.shapes(LayerSiN).insert(Si_slab)


        # add the left bus pin
        xp1 = -0.05 / self.layout.dbu
        xp2 = 0.05 / self.layout.dbu
        yp1 = 0
        xa = -beam_l
        xb = beam_l
        p1 = [Point(xa + xp2, yp1), Point(xa + xp1, yp1)]
        p1c = Point(xa, yp1)
        self.set_p1 = p1c
        self.p1 = p1c

        pin = Path(p1, w)
        shapes(LayerPinRecN).insert(pin)
        t = Trans(Trans.R0, xa, yp1)
        text = Text("opt1", t)
        shape = shapes(LayerPinRecN).insert(text)
        shape.text_size = 0.4 / dbu

        # add the right bus pin
        p2 = [Point(xb + xp1, yp1), Point(xb + xp2, yp1)]
        p2c = Point(xb, yp1)
        self.set_p2 = p2c
        self.p2 = p2c

        pin = Path(p2, w)
        shapes(LayerPinRecN).insert(pin)
        t = Trans(Trans.R0, xb, yp1)
        text = Text("opt2", t)
        shape = shapes(LayerPinRecN).insert(text)
        shape.text_size = 0.4 / dbu

        layer_temp = self.layout.layer(LayerInfo(913, 0))
        shapes_temp = self.cell.shapes(layer_temp)
        ShapeProcessor().merge(self.layout, self.cell, LayerSiN, shapes_temp, True, 0, True, True)
        self.cell.shapes(LayerSiN).clear()
        shapes_SiN = self.cell.shapes(LayerSiN)
        ShapeProcessor().merge(self.layout, self.cell, layer_temp, shapes_SiN, True, 0, True, True)
        self.cell.shapes(layer_temp).clear()

        # w = int(round(self.w/dbu))
        dev = Box(xa, -w * 4, xb, w * 4)
        shapes(LayerDevRecN).insert(dev)

        shapeClad = pya.Region()
        shapeClad += shapes_SiN
        region_devrec = Region(dev)
        region_devrec2 = Region(dev).size(2500)
        shapeClad = shapeClad.size(2000) - (region_devrec2 - region_devrec)
        shapes(LayerCladN).insert(shapeClad)
     
        layer_temp = self.layout.layer(LayerInfo(914, 0))
        shapes_temp = self.cell.shapes(layer_temp)
        ShapeProcessor().merge(self.layout, self.cell, LayerCladN, shapes_temp, True, 0, True, True)

        # Clear original LayerCladN and insert merged result back
        self.cell.shapes(LayerCladN).clear()
        ShapeProcessor().merge(self.layout, self.cell, layer_temp, self.cell.shapes(LayerCladN),True, 0, True, True)

        # Clean up temp layer
        self.cell.shapes(layer_temp).clear()