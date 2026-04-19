# Waveguide Bragg grating
# imported from SiEPIC_EBeam_PDK.  Model does not exist. Layout only.

from . import *
import pya
from pya import *
import numpy as np
class ebeam_pcell_fractal_nanowire_extra(pya.PCellDeclarationHelper):
  def __init__(self):
    super(ebeam_pcell_fractal_nanowire_extra, self).__init__()

    from SiEPIC.utils import get_technology_by_name
    self.technology_name = 'SiEPICfab_EBeam_ZEP'
    TECHNOLOGY = get_technology_by_name(self.technology_name)
    self.TECHNOLOGY = TECHNOLOGY

    self.param("layer", self.TypeLayer, "Layer - NW", default=TECHNOLOGY['NbTiN'])
    self.param("LayerMetal", self.TypeLayer, "Au/Ti Layer", default=TECHNOLOGY['Ti/Au'])
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default=TECHNOLOGY['PinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default=TECHNOLOGY['DevRec'])
    self.param("radius_scale", self.TypeDouble, "radius scale (4 minimum)", default = 4)
    self.param("nw_width", self.TypeDouble, "NW width (microns)", default=0.05)
    self.param("l", self.TypeDouble, "NW length (microns)", default=10.0)
  def coerce_parameters_impl(self):
    pass
    
  def display_text_impl(self):
    return "NbTiN fractal extra(w" + ('%.3f' % int(self.nw_width)) +"_scale"+('%.3f' % int(self.radius_scale))+ "_l" + ('%.3f' % int(self.l)) + ")"
    
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

    theta_main = np.linspace(-np.pi / 4, 5 / 4 * np.pi, int(3 / 2 * n))
    theta_l1 = np.linspace(-3 / 4 * np.pi, np.pi / 4, 2*n)[::-1]
    theta_l2 = np.linspace(np.pi / 4, 3 / 4 * np.pi, n)
    
        # -------------------------------
    # Length calculations (arc length form)
    # -------------------------------

    # Angular spans in radians
    delta_theta_main = theta_main[-1] - theta_main[0]       # 5π/4 - (–π/4) = 3π/2
    delta_theta_l1   = theta_l1[0] - theta_l1[-1]           # reversed: π/4 – (–3π/4) = π
    delta_theta_l2   = theta_l2[-1] - theta_l2[0]           # 3π/4 – π/4 = π/2

    # Midline radius between r1 and r2
    r_mid = (r1 + r2) / 2

    # Arc length for each segment
    L_main = r_mid * delta_theta_main
    L_l1   = r_mid * delta_theta_l1
    L_l2   = r_mid * delta_theta_l2
    L_r1   = L_l1
    L_r2   = L_l2

    # Approximated: l3 = half of l1, l4 = same as l2, l5 = half of l2
    L_l3 = L_l1 / 2
    L_r3 = L_l3
    L_l4 = L_l2
    L_r4 = L_l4
    L_l5 = L_l2 / 2
    L_r5 = L_l5

    # Total centerline length
    L_total_dbu = L_main + L_l1 + L_l2 + L_l3 + L_l4 + L_l5 + L_r1 + L_r2 + L_r3 + L_r4 + L_r5
    L_total_um = L_total_dbu

    # Adjust l (in dbu) to account for total arc length
    l = l - L_total_dbu


    # Function to generate coordinates for segments
    def generate_segment_coords(radius, theta, offset_x=0, offset_y=0):
        x = radius * np.cos(theta) + offset_x
        y = radius * np.sin(theta) + offset_y
        return x, y

    # Recursive function to apply offset from the last segment's endpoint
    def generate_offset_coords(radius, theta, previous_x, previous_y, angle_offset):
        offset_x = radius * np.cos(angle_offset) + previous_x[-1]
        offset_y = radius * np.cos(angle_offset) + previous_y[-1]
        x, y = generate_segment_coords(radius, theta, offset_x, offset_y)
        return x, y

    # Main curves
    x1, y1 = generate_segment_coords(r1, theta_main)
    x2, y2 = generate_segment_coords(r2, theta_main)

    # Left-side segments (with recursive offset propagation)
    x1_l, y1_l = generate_offset_coords(r2, theta_l1, x1, y1, theta_main[-1])
    x2_l, y2_l = generate_offset_coords(r1, theta_l1, x2, y2, theta_main[-1])

    x1_l2, y1_l2 = generate_offset_coords(r1, theta_l2, x1_l, y1_l, theta_l1[-1])
    x2_l2, y2_l2 = generate_offset_coords(r2, theta_l2, x2_l, y2_l, theta_l1[-1])

    x1_l3 = x1_l[len(x1_l)//2:] - 2*(r2+r1)*np.cos(np.pi/4)
    y1_l3 = y1_l[len(y1_l)//2:]

    x2_l3 = x2_l[len(x2_l)//2:]  - 2*(r2+r1)*np.cos(np.pi/4)
    y2_l3 = y2_l[len(y2_l)//2:]


    x1_l4 = x1_l2 - 2*(r2+r1)*np.cos(np.pi/4)
    y1_l4 = y1_l2

    x2_l4 = x2_l2  - 2*(r2+r1)*np.cos(np.pi/4)
    y2_l4 = y2_l2

    x1_l5 = x1_l4[len(x1_l3)//2:]
    y1_l5 = y1_l4[len(x1_l3)//2:]

    x2_l5 = x2_l4[len(x2_l3)//2:]
    y2_l5 = y2_l4[len(x1_l3)//2:]



    # Define the rotation angle (45 degrees counterclockwise)
    theta = np.pi / 4  # 45 degrees in radians

    # Define the rotation matrix
    rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)], 
                                [np.sin(theta),  np.cos(theta)]])

    # Combine x and y vectors into a coordinate array for rotation
    coords_l5_1 = np.vstack((x1_l5, y1_l5))  # Shape: (2, N)
    coords_l5_2 = np.vstack((x2_l5, y2_l5))  # Shape: (2, N)

    # Apply the rotation matrix
    rotated_coords_l5_1 = rotation_matrix @ coords_l5_1
    rotated_coords_l5_2 = rotation_matrix @ coords_l5_2

    # Unpack the rotated coordinates
    x1_l5, y1_l5 = rotated_coords_l5_1[0], rotated_coords_l5_1[1]
    x2_l5, y2_l5 = rotated_coords_l5_2[0], rotated_coords_l5_2[1]

    x1_l5 = x1_l5 - (np.abs(x1_l4[-1]) - np.abs(x1_l5[0]))
    y1_l5 = y1_l5 - (np.abs(y1_l4[-1]) - np.abs(y1_l5[0]))

    x2_l5 = x2_l5 - (np.abs(x2_l4[-1]) - np.abs(x2_l5[0]))
    y2_l5 = y2_l5 - (np.abs(y2_l4[-1]) - np.abs(y2_l5[0]))


    # x1_l3 = x1_l[len(x1_l)//2:] - 2*(r2+r1)*np.cos(np.pi/4)
    # y1_l3 = y1_l[len(y1_l)//2:]

    # x2_l3 = x2_l[len(x2_l)//2:]  - 2*(r2+r1)*np.cos(np.pi/4)
    # y2_l3 = y2_l[len(y2_l)//2:]


    # x1_l4 = x1_l2[:len(x1_l2)//2] - 2*(r2+r1)*np.cos(np.pi/4)
    # y1_l4 = y1_l2[:len(x1_l2)//2]
    # x2_l4 = x2_l2[:len(x1_l2)//2]  - 2*(r2+r1)*np.cos(np.pi/4)
    # y2_l4 = y2_l2[:len(x1_l2)//2]


    # Right-side segments (mirroring the left)
    x1_r, y1_r = -x1_l, y1_l
    x2_r, y2_r = -x2_l, y2_l
    x1_r2, y1_r2 = -x1_l2, y1_l2
    x2_r2, y2_r2 = -x2_l2, y2_l2
    x1_r3 = -x1_l3
    y1_r3 = y1_l3
    x2_r3 = -x2_l3
    y2_r3 = y2_l3
    x1_r4 = -x1_l4
    y1_r4 = y1_l4
    x2_r4 = -x2_l4
    y2_r4 = y2_l4
    x1_r5 = -x1_l5
    y1_r5 = y1_l5
    x2_r5 = -x2_l5
    y2_r5 = y2_l5




    # Concatenate all x and y coordinates separately
    x_all_1 = np.concatenate([x1_l5[::-1], x1_l4[::-1], x1_l3[::-1], x1_l2[::-1], x1_l[::-1], x1[::-1], x1_r, x1_r2, x1_r3, x1_r4, x1_r5])
    y_all_1 = np.concatenate([y1_l5[::-1], y1_l4[::-1], y1_l3[::-1], y1_l2[::-1], y1_l[::-1], y1[::-1], y1_r, y1_r2, y1_r3, y1_r4, y1_r5])

    x_all_2 = np.concatenate([x2_l5[::-1], x2_l4[::-1], x2_l3[::-1], x2_l2[::-1], x2_l[::-1], x2[::-1], x2_r, x2_r2, x2_r3, x2_r4, x2_r5])[::-1]
    y_all_2 = np.concatenate([y2_l5[::-1], y2_l4[::-1], y2_l3[::-1], y2_l2[::-1], y2_l[::-1], y2[::-1], y2_r, y2_r2, y2_r3, y2_r4, y2_r5])[::-1]

    # Combine the two sets of coordinates into one continuous set
    x_final = np.concatenate([x_all_1, x_all_2])
    y_final = np.concatenate([y_all_1, y_all_2])

    # Vertically stack the final points
    final_points = np.vstack((x_final, y_final-np.min(y_final))).T
    fractal = pya.Region()  
    pts1 = [Point(x, y) for x, y in zip(final_points[:, 0], final_points[:, 1] +l/2)]
    fractal.insert(Polygon(pts1))


    square1 = pya.Region()  
    #W = radius + 0.0005/dbu+w/2
    W = -np.min(x_final)
    square1.insert(pya.Box(-W, -l/2, W, l/2)) #pya.Point(w/2+0.35,l/2), pya.Point(w/2+0.35,-l/2), pya.Point(0.35-w/2,l/2-s), pya.Point(w/2,l/2-s), pya.Point(w/2,-l/2)])
    #self.cell.shapes(LayerSiN).insert(square1)

    square2 = pya.Region()
    #W_2 = radius+ 0.0005/dbu-w/2
    W_2 = W - nw_width
    square2.insert(pya.Box(-W_2, -l/2, W_2, l/2 ))
    #self.cell.shapes(LayerSiN).insert(square2)

    taper1 = pya.Region()
    taper1.insert(pya.Polygon([Point(-W, -l/2), Point(-W+w,-l/2), Point(-W+w-2/dbu,-l/2-10/dbu), Point(-W-7/dbu,-l/2-10/dbu)]))
    
    taper2 = pya.Region()
    taper1.insert(pya.Polygon([Point(W, -l/2), Point(W-w,-l/2), Point(W-w+2/dbu,-l/2-10/dbu), Point(W+7/dbu,-l/2-10/dbu)]))
    
    taper1_extra = pya.Region()
    taper1_extra.insert(pya.Polygon([Point(-W - 0.02/dbu, -l/2), Point(-W+w + 0.02/dbu,-l/2), Point(-W+w-2/dbu,-l/2-10/dbu), Point(-W-7/dbu,-l/2-10/dbu)]))
    
    taper2_extra = pya.Region()
    taper2_extra.insert(pya.Polygon([Point(W+ 0.02/dbu, -l/2), Point(W-w - 0.02/dbu,-l/2), Point(W-w+2/dbu,-l/2-10/dbu), Point(W+7/dbu,-l/2-10/dbu)]))
    
    
    
    full_shape = square1 - square2 + fractal + taper1 + taper2
    overlap = taper1_extra + taper2_extra
    self.cell.shapes(LayerSiN).insert(full_shape)
    self.cell.shapes(LayerMetal).insert(overlap)
    
    # Pins on the nanowire end:
    pin = Path([Point(-W+w/2-4.5/dbu,-l/2-10/dbu+w), Point(-W+w/2-4.5/dbu, -w-l/2-10/dbu)], w+5/dbu)
    shapes(LayerPinRecN).insert(pin)
    text = Text ("pin2", Trans(Trans.R270, -W+w/2-4.5/dbu, -l/2-10/dbu))
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu

    pin = Path([Point(W-w/2+4.5/dbu,-l/2-10/dbu+w),Point(W-w/2+4.5/dbu, -w-l/2-10/dbu)], w+5/dbu)
    shapes(LayerPinRecN).insert(pin)
    text = Text ("pin1", Trans(Trans.R270, W-w/2+4.5/dbu, -l/2-10/dbu))
    shape = shapes(LayerPinRecN).insert(text)
    shape.text_size = 0.4/dbu
    radius = W

    #draw devrec box
    devrec_box = [Point(-2*(radius+2*w),-l/2),Point(2*(radius+2*w),-l/2),Point(2*(radius+2*w),l/2),Point(-2*(radius+2*w),l/2)]
    #place devrec box
    shapes(LayerDevRecN).insert(Polygon(devrec_box))
    
    t = Trans(Trans.R270, radius, l/4)
    text = Text ('NbTiNnanowire:w=%.3fu r_scale=%.3fu l=%.3fu'%(int(self.nw_width)*1000,int(self.radius_scale)*1000,int(self.l)*1000), t)
    shape = shapes(LayerDevRecN).insert(text)
    shape.text_size = 0.5/dbu