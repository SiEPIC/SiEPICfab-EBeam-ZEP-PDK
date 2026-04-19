# Waveguide Bragg grating
# imported from SiEPIC_EBeam_PDK.  Model does not exist. Layout only.

from . import *
import pya
from pya import *
import numpy as np
class ebeam_pcell_halfcircle_nanowire(pya.PCellDeclarationHelper):
  def __init__(self):
      super(ebeam_pcell_halfcircle_nanowire, self).__init__()

      from SiEPIC.utils import get_technology_by_name
      self.technology_name = 'SiEPICfab_EBeam_ZEP'
      TECHNOLOGY = get_technology_by_name(self.technology_name)
      self.TECHNOLOGY = TECHNOLOGY

      # Override NbTiN to hardcoded 1/69
      self.param("layer", self.TypeLayer, "Layer - NW", default=TECHNOLOGY['NbTiN'])
      self.param("LayerMetal", self.TypeLayer, "Au/Ti Layer", default=TECHNOLOGY['Ti/Au'])
      self.param("pinrec", self.TypeLayer, "PinRec Layer", default=TECHNOLOGY['PinRec'])
      self.param("devrec", self.TypeLayer, "DevRec Layer", default=TECHNOLOGY['DevRec'])

      self.param("nw_width", self.TypeDouble, "NW width (microns)", default=0.05)
      self.param("l", self.TypeDouble, "NW length (microns)", default=10.0)
      self.param("radius_scale", self.TypeDouble, "radius scale (4 minimum)", default = 4)

  def coerce_parameters_impl(self):
    pass
    
  def display_text_impl(self):
    return "NbTiN halfcircle nw(w" + ('%.3f' % int(self.nw_width)) +"_scale"+('%.3f' % int(self.radius_scale))+ "_l" + ('%.3f' % int(self.l)) + ")"
    
  def can_create_from_shape(self, layout, shape, layer):
    return False
    
  def produce_impl(self):
  
    # fetch the parameters
    dbu = self.layout.dbu
    ly = self.layout
    from math import pi, cos, sin, log, sqrt, acos

    LayerSi = self.layer
    LayerSiN = ly.layer(LayerSi)
    LayerSi = self.layer
    LayerSiN = ly.layer(LayerSi)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
    LayerMetal = self.LayerMetal #Ti/Au layer
    LayerMetal = ly.layer(LayerMetal)
    nw_width = self.nw_width/dbu
    w = nw_width
    l = self.l/dbu
    radius_scale = self.radius_scale
    shapes = self.cell.shapes
    
    ###Fractal NW

    # Parameters
    n = 25
    r1 = nw_width * radius_scale
    r2 = r1 + nw_width

    # Define angle segments
    theta_main = np.linspace(0,np.pi, n)
    theta_l1 = np.linspace(3/2*np.pi, 2*np.pi, n)
    
    
        # -------------------------------
    # Length calculations (in microns)
    # -------------------------------

    # Angular spans
    delta_theta_main = theta_main[-1] - theta_main[0]     # π
    delta_theta_l1   = theta_l1[-1] - theta_l1[0]         # π/2

    # Midline radius
    r_mid = (r1 + r2) / 2

    # Lengths (in dbu)
    L_main = r_mid * delta_theta_main
    L_l1   = r_mid * (delta_theta_l1)  # Left loop
    L_r1   = L_l1                      # Right loop is mirrored

    # Total
    L_total_dbu = L_main + L_l1 + L_r1
    L_total_um  = L_total_dbu
    l = l - L_total_um
    # Function to generate coordinates for segments
    def generate_segment_coords(radius, theta, offset_x=0, offset_y=0):
        x = radius * np.cos(theta) + offset_x
        y = radius * np.sin(theta) + offset_y
        return x, y
    
    # Main curves
    x1, y1 = generate_segment_coords(r1, theta_main)
    x2, y2 = generate_segment_coords(r2, theta_main)
    
    # # Left-side segments (with recursive offset propagation)
    x1_l, y1_l = generate_segment_coords(r2, theta_l1, offset_x = x1[-1]-r1-nw_width)
    x2_l, y2_l = generate_segment_coords(r1, theta_l1, offset_x = x2[-1]-r2+nw_width)
    
    
    # Right-side segments (mirroring the left)
    x1_r, y1_r = -x1_l, y1_l
    x2_r, y2_r = -x2_l, y2_l
    
    x_all_1 = np.concatenate([x1_l, x1[::-1], x1_r[::-1]])
    y_all_1 = np.concatenate([y1_l, y1[::-1], y1_r[::-1]])
    
    x_all_2 = np.concatenate([x2_l, x2[::-1], x2_r[::-1]])[::-1]
    y_all_2 = np.concatenate([y2_l, y2[::-1], y2_r[::-1]])[::-1]
    
    
    # Combine the two sets of coordinates into one continuous set
    
    x_final = np.concatenate([x_all_1, x_all_2])
    y_final = np.concatenate([y_all_1, y_all_2])  - (np.min(y_all_1) + np.min(y_all_2))/2
    
    # Vertically stack the final points
    final_points = np.vstack((x_final, y_final)).T

    fractal = pya.Region()  
    pts1 = [Point(x, y) for x, y in zip(final_points[:, 0], final_points[:, 1])]
    fractal.insert(Polygon(pts1))


    square1 = pya.Region()  
    #W = radius + 0.0005/dbu+w/2
    W = -np.min(x_all_1)
    
    square1.insert(pya.Box(-l/2 , nw_width/2, -W, -nw_width/2 )) #pya.Point(w/2+0.35,l/2), pya.Point(w/2+0.35,-l/2), pya.Point(0.35-w/2,l/2-s), pya.Point(w/2,l/2-s), pya.Point(w/2,-l/2)])
    #self.cell.shapes(LayerSiN).insert(square1)

    square2 = pya.Region()
    #W_2 = radius+ 0.0005/dbu-w/2
    square2.insert(pya.Box(l/2 , nw_width/2, W, -nw_width/2 ))
    #self.cell.shapes(LayerSiN).insert(square2)

    taper1 = pya.Region()
    taper1.insert(pya.Polygon([Point(-l/2, nw_width/2), Point(-l/2, -nw_width/2), Point(-(l/2 + 10/dbu), nw_width/2 + 2/dbu), Point(-(l/2 + 10/dbu), -nw_width/2 + 7/dbu)]))

    taper2 = pya.Region()
    taper1.insert(pya.Polygon([Point(l/2, nw_width/2), Point(l/2, -nw_width/2), Point(l/2 + 10/dbu, nw_width/2 + 2/dbu), Point(l/2 + 10/dbu, -nw_width/2 + 7/dbu)]))

    full_shape = square1 + square2 + fractal + taper1 + taper2
    taper1_extra = pya.Region()
    taper1_extra.insert(pya.Polygon([Point(-l/2, nw_width/2 + 0.02/dbu), Point(-l/2, -nw_width/2 - 0.02/dbu), Point(-(l/2 + 10/dbu), nw_width/2 + 2/dbu), Point(-(l/2 + 10/dbu), -nw_width/2 + 7/dbu)]))

    taper2_extra = pya.Region()
    taper2_extra.insert(pya.Polygon([Point(l/2, nw_width/2 +0.02/dbu), Point(l/2, -nw_width/2 - 0.02/dbu), Point(l/2 + 10/dbu, nw_width/2 + 2/dbu), Point(l/2 + 10/dbu, -nw_width/2 + 7/dbu)]))

    
    overlap = taper1_extra + taper2_extra
    self.cell.shapes(LayerSiN).insert(full_shape)
    self.cell.shapes(LayerMetal).insert(overlap)

    #draw devrec box
    devrec_box = [Point(l/2 + 10/dbu, -nw_width/2 - 0.02/dbu),Point(-(l/2 + 10/dbu), -nw_width/2 - 0.02/dbu), Point(-(l/2 + 10/dbu), -nw_width/2 + 7/dbu), Point(l/2 + 10/dbu, -nw_width/2 + 7/dbu)]
    #place devrec box	
    
    shapes(LayerDevRecN).insert(Polygon(devrec_box))
    
    t = Trans(Trans.R270, r1, l/4)
    text = Text ('NbTiNnanowire:w=%.3fu r_scale=%.3fu l=%.3fu'%(int(self.nw_width)*1000,int(self.radius_scale)*1000,int(self.l)*1000), t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = 0.5/dbu
      