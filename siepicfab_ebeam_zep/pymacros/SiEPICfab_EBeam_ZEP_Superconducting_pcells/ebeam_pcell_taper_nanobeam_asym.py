# from . import *
import pya
from pya import *
import math


class ebeam_pcell_taper_nanobeam_asym(pya.PCellDeclarationHelper):
    """
    Input: length, width
    """

    def __init__(self):
        # Important: initialize the super class
        super(ebeam_pcell_taper_nanobeam_asym, self).__init__()
        from SiEPIC.utils import get_technology_by_name, load_Waveguides_by_Tech
        self.technology_name = 'SiEPICfab_EBeam_ZEP'
        TECHNOLOGY = get_technology_by_name(self.technology_name)
        self.TECHNOLOGY = TECHNOLOGY

        # Load all strip waveguides
        waveguide_types = load_Waveguides_by_Tech(self.technology_name)

        self.param("w", self.TypeDouble, "Waveguide width (microns)", default=0.5)
        self.param("s", self.TypeDouble, "Cavity length (microns)", default=5)
        self.param("wg_l", self.TypeDouble, "Straight Waveguide length (microns)", default=0)
        
        self.param("n3", self.TypeInt, "Number of unchanged holes", default=9)
        self.param("n2", self.TypeInt, "Number of tapered holes", default=1)
        self.param("n1", self.TypeInt, "Number of tapered holes up", default=3)
        self.param("r_max_b", self.TypeDouble, "maximum raduis on back reflector", default=100)
        self.param("r_min", self.TypeDouble, "minimum radius", default=50)
        self.param("r_max_f", self.TypeDouble, "maximum raduis on front reflector", default=70)

        self.param("n_vertices", self.TypeInt, "Vertices of a hole", default=32)
        self.param("layer", self.TypeLayer, "Layer - Waveguide", default=TECHNOLOGY['Si_core'])
        self.param("cladlayer", self.TypeLayer, "Cladding Layer", default=TECHNOLOGY['Si_clad'])
        self.param("pinrec", self.TypeLayer, "PinRec Layer", default=TECHNOLOGY['PinRec'])
        self.param("devrec", self.TypeLayer, "DevRec Layer", default=TECHNOLOGY['DevRec'])
        self.param("etch", self.TypeLayer, "oxide etch layer", default=TECHNOLOGY['Si_etch_highres'])
        self.param("extra_Si", self.TypeLayer, "Extra Si Layer", default=TECHNOLOGY['Si_etch_highres_nobias'])

    def display_text_impl(self):
        return "nanobeam_cavity_%.2f_%.2f" % (self.w, self.s)

    def coerce_parameters_impl(self):
        pass

    def can_create_from_shape(self, layout, shape, layer):
        return False

    def produce_impl(self):
        import numpy as np
        import scipy as sp
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
        n3 = self.n3
        r_max_b = self.r_max_b
        r_min = self.r_min
        r_max_f = self.r_max_f
        n_vertices = self.n_vertices
        wg_l = self.wg_l / dbu

        # function to generate points to create a circle
        def circle(x, y, r):
            npts = n_vertices
            theta = 2 * math.pi / npts  # increment, in radians
            pts = []
            for i in range(0, npts):
                pts.append(Point.from_dpoint(DPoint((x + r * math.cos(i * theta)) / 1, (y + r * math.sin(i * theta)) / 1)))
            return pts

        def cross(params):
            # Split params into top and left
            n_top = len(params) // 2
            params_top = params[:n_top]
            params_left = params[n_top:]

            y_end_left = params_left[-1]
            x_end_left = 0 - y_end_left
            x_end_top = params_top[-1]
            y_end_top = 0 - x_end_top

            # Define the left arm
            points_x_left = np.linspace(-2.5e-6, y_end_top, len(params_left) + 1)
            points_y_left = np.concatenate(([0.25e-6], params_left))
            n_interp = 50
            polygon_x_left = np.linspace(points_x_left.min(), points_x_left.max(), n_interp)
            interpolator_left = interpolate.interp1d(points_x_left, points_y_left, kind='cubic')
            polygon_y_left = np.clip(interpolator_left(polygon_x_left), -1e-6, 1e-6)
            pplu = [(x, y) for x, y in zip(polygon_x_left, polygon_y_left)]
            ppld = [(x, -y) for x, y in zip(polygon_x_left, polygon_y_left)]
            pprd = [(-x, -y) for x, y in zip(polygon_x_left, polygon_y_left)]
            ppru = [(-x, y) for x, y in zip(polygon_x_left, polygon_y_left)]

            # Define the top arm
            points_x_top = np.concatenate(([0.05e-6], params_top))
            points_y_top = np.linspace(-1e-6, x_end_left, len(params_top) + 1)
            polygon_y_top = np.linspace(points_y_top.min(), points_y_top.max(), n_interp)
            interpolator_top = interpolate.interp1d(points_y_top, points_x_top, kind='cubic')
            polygon_x_top = np.clip(interpolator_top(polygon_y_top), -0.5e-6, 0.5e-6)

            ppur = [(x, -y) for x, y in zip(polygon_x_top, polygon_y_top)]
            ppul = [(-x, -y) for x, y in zip(polygon_x_top, polygon_y_top)]
            ppdl = [(-x, y) for x, y in zip(polygon_x_top, polygon_y_top)]
            ppdr = [(x, y) for x, y in zip(polygon_x_top, polygon_y_top)]

            polygon_points = (
                pplu[::-1] + ppld + ppdl[::-1] + ppdr +
                pprd[::-1] + ppru + ppur[::-1] + ppul
            )
            return polygon_points
        

        params = np.array([5.22384374e-08, 6.06573970e-08, 6.79309922e-08, 7.64681666e-08, 8.56607337e-08, 9.63837579e-08, 9.07179214e-08, 1.17283562e-07, 6.75093045e-08, 1.14334779e-07, 2.50000000e-07, 2.64800153e-07, 3.12030533e-07, 3.10153662e-07, 3.40728375e-07, 3.70093523e-07, 4.03195069e-07, 4.17789421e-07, 4.35302368e-07, 3.89936820e-07])
       # params = params * 1e6 / dbu

        # Taper Silicon core Layer
        Si_taper = Region()
        taper_pts_list = cross(params)
        taper_pts = [Point.from_dpoint(DPoint(x * 1e6 / dbu, y * 1e6 / dbu)) for x, y in taper_pts_list]
        Si_taper.insert(Polygon(taper_pts))
        taper = Si_taper
        self.cell.shapes(LayerSiN).insert(taper)

                # Taper Silicon clad Layer
        # Offset all y-values by ±2 µm depending on their sign
        clad_offset_um = 2e-6
        taper_pts_clad = []
        for x, y in taper_pts_list:
            if y >= 0:
                y_clad = y + clad_offset_um
            else:
                y_clad = y - clad_offset_um
            taper_pts_clad.append(Point(int(round(x * 1e6 / dbu)), int(round(y_clad * 1e6 / dbu))))

                

        # raster through all holes with shifts and waveguide front reflector
        r_list_taper_up = np.linspace(r_min, r_max_f, n1+1)[:-1]
        r_list_taper_down = r_list_taper_up[::-1]
        r_list_plateau = np.full(n2, r_max_f)

        r = np.concatenate([r_list_taper_up, r_list_plateau, r_list_taper_down])

        x_pos = [s / 2]
        for i in range(1, len(r)):
            r_avg = 0.5 * (r[i - 1] + r[i])
            x_pos.append(x_pos[i - 1] + 1.22 * r_avg + 308)
        r_pos = r



        r_list_taper_up = np.linspace(r_min, r_max_b, n1+1)[:-1]
        r_list_plateau = np.full(n3, r_max_b)

        r = np.concatenate([r_list_taper_up, r_list_plateau])
        x_neg = [-s / 2]
        for i in range(1, len(r)):
            r_avg = 0.5 * (r[i - 1] + r[i])
            x_neg.append(x_neg[i - 1] - (1.22 * r_avg + 308))
        r_neg = r

        x_all = x_neg + x_pos
        r_all = list(r_neg) + list(r_pos)

        hole = Region()
        for i in range(len(r_all)):
            hole_poly = Polygon(circle(0, 0, r_all[i]))
            hole.insert(hole_poly.transformed(Trans(Trans.R0, x_all[i], 0)))
        self.cell.shapes(LayerHighResHoles).insert(hole)

        Si_slab = Region()
        hole_x_min = np.min(x_all) - wg_l
        hole_x_max = np.max(x_all) + wg_l
        Si_slab.insert(Box(hole_x_min, -w / 2, -s/2, w / 2))
        Si_slab.insert(Box(s/2, -w / 2, hole_x_max, w / 2))
        Si_slab.insert(Box(-0.05/dbu, 1/dbu, 0.05/dbu,3/dbu))
        Si_slab.insert(Box(-0.05/dbu, -1/dbu, 0.05/dbu,-3/dbu))
        Si_slab.insert(Box(0, -w / 2, hole_x_max, w / 2))
        anchor_l = 8 / dbu
        phc = Si_slab
        self.cell.shapes(LayerSiN).insert(phc)

        # add the left bus pin
        xp1 = -0.05 / self.layout.dbu
        xp2 = 0.05 / self.layout.dbu
        yp1 = 0
        xa = hole_x_min
        xb = hole_x_max
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
        uppercross1 = Box(-2/dbu, 1/dbu, 2/dbu,5/dbu)
        uppercross12 = Box(-2/dbu, -1/dbu, 2/dbu,-5/dbu)



        Si_taper = Region()
        Si_taper.insert(Polygon(taper_pts_clad))
        taper = Si_taper
        self.cell.shapes(LayerCladN).insert(taper)
        self.cell.shapes(LayerCladN).insert(uppercross1)
        self.cell.shapes(LayerCladN).insert(uppercross12)

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