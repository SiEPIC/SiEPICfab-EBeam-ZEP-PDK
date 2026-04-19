# Waveguide Bragg grating
# imported from SiEPIC_EBeam_PDK.  Model does not exist. Layout only.

from . import *
import pya
from pya import *
import math
class ebeam_pcell_wideRound_NW_modified(pya.PCellDeclarationHelper):
  def __init__(self):
    super(ebeam_pcell_wideRound_NW_modified , self).__init__()

    from SiEPIC.utils import get_technology_by_name
    self.technology_name = 'SiEPICfab_EBeam_ZEP'
    TECHNOLOGY = get_technology_by_name(self.technology_name)
    self.TECHNOLOGY = TECHNOLOGY

    # Override NbTiN to hardcoded 1/69
    self.param("layerNbTiN", self.TypeLayer, "Layer - NW", default=TECHNOLOGY['NbTiN'])
    self.param("layer", self.TypeLayer, "Core Layer", default=TECHNOLOGY['Si_core'])
    self.param("layerClad", self.TypeLayer, "Clad Layer", default=TECHNOLOGY['Si_clad'])
    self.param("LayerMetal", self.TypeLayer, "Au/Ti Layer", default=TECHNOLOGY['Ti/Au']) 
    self.param("pinrec", self.TypeLayer, "PinRec Layer", default=TECHNOLOGY['PinRec'])
    self.param("devrec", self.TypeLayer, "DevRec Layer", default=TECHNOLOGY['DevRec'])
    self.param("eblregion", self.TypeLayer, "EBL Region Layer", default=TECHNOLOGY['EBL-Regions'])
    self.param("photonic_layer", self.TypeInt, "Photonic Layer (1=true 0= false)", default=1)
    self.param("wg", self.TypeDouble, "Waveguide width (microns)", default = 0.50)
    self.param("w", self.TypeDouble, "NW width (microns)", default = 0.05)
    self.param("l", self.TypeDouble, "NW length (microns)", default = 80)
    self.param("bend_w", self.TypeDouble, "Bend Width (microns)", default = 0.05)
    self.param("radius", self.TypeDouble, "radius (microns)", default = 0.125)
    self.param("n_vertices", self.TypeInt, "Vertices of a hole", default = 128)
    

  def coerce_parameters_impl(self):
    pass
    
  def display_text_impl(self):
    return "NbTiNnanowire(w" + ('%.1f' % float(self.w*1000)) +"nm_r"+('%.1f' % float(self.radius*1000))+ "nm_l" + ('%.2f' % float(self.l)) + "um)"

  def can_create_from_shape(self, layout, shape, layer):
    return False
    
  def produce_impl(self):
    dbu = self.layout.dbu
    ly = self.layout
    from math import pi, cos, sin,tan


    LayerSi = self.layer
    LayerSiN = ly.layer(LayerSi)
    LayerNbTiN = ly.layer(self.layerNbTiN)
    LayerCladN = ly.layer(self.layerClad)
    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
    LayerMetal = self.LayerMetal #Ti/Au layer
    LayerMetal = ly.layer(LayerMetal)
    photonic_layer = self.photonic_layer
    eblregion = ly.layer(self.eblregion)

    w = self.w / dbu
    wg = self.wg / dbu
    l = self.l / dbu
    radius = self.radius / dbu
    bend_w = self.bend_w / dbu
    n_vertices = self.n_vertices

    shapes = self.cell.shapes

    if photonic_layer:
      clad_width = wg/2 + 2/dbu
      #Make the photonic layer first
      wg_square = Region(Box(-wg/2, -l/2, wg/2, l/2 + 1/dbu))
      shapes(LayerSiN).insert(wg_square)


      wg_clad_square = Region(Box(-clad_width, -l/2, clad_width, l/2 + 1/dbu))
        # Metal overlap
      outer_taper = Region(Polygon([
          Point(-clad_width, -l/2+2/dbu*tan(pi/4)),
          Point(clad_width, -l/2+2/dbu*tan(pi/4)),
          Point(26 / dbu, -l/2 - 12 / dbu+2/dbu*sin(pi/4)),
          Point(26 / dbu, -l/2 - 22 / dbu),
          Point(-26 / dbu, -l/2 - 22 / dbu),
          Point(-26 / dbu, -l/2 - 12 / dbu+2/dbu*sin(pi/4)),
      ]))
      inner_taper = Region(Polygon([
          Point(-wg/2, -l/2),
          Point(wg/2, -l/2),
          Point(24 / dbu, -l/2 - 12 / dbu),
          Point(24 / dbu, -l/2 - 22 / dbu),
          Point(-24 / dbu, -l/2 - 22 / dbu),
          Point(-24 / dbu, -l/2 - 12 / dbu),
      ]))
      clad_shape = outer_taper - inner_taper + wg_clad_square
      shapes(LayerCladN).insert(clad_shape)





    W = radius + 0.0005 / dbu + w
    W_2 = radius + 0.0005 / dbu
    Y = l / 2 - radius - bend_w

    # Rectangle: full body
    square1 = Region(Box(-W, -l/2, W, l/2))

    # Rectangle: vertical center cutout
    square2 = Region(Box(-W_2, -l/2, W_2, Y))



    # Arch: half-circle cutout at top
    theta = 2 * pi / n_vertices
    arc_pts = [
        Point.from_dpoint(DPoint(radius * cos(i * theta), radius * sin(i * theta) + Y))
        for i in range(n_vertices)
    ]
    arch_poly = Polygon(arc_pts)
    curve = Region(arch_poly)

    # Tapers
    taper1_poly = Polygon([
        Point(-W, -l/2),
        Point(-W + w, -l/2),
        Point(-W + w - 2 / dbu, -l/2 - 10 / dbu),
        Point(-W - 7 / dbu, -l/2 - 10 / dbu)
    ])
    taper2_poly = Polygon([
        Point(W, -l/2),
        Point(W - w, -l/2),
        Point(W - w + 2 / dbu, -l/2 - 10 / dbu),
        Point(W + 7 / dbu, -l/2 - 10 / dbu)
    ])


    
    tapers = Region()
    tapers.insert(taper1_poly)
    tapers.insert(taper2_poly)

    # Final shape
    wire_shape = square1 - square2 - curve + tapers
    shapes(LayerNbTiN).insert(wire_shape)
    shapes(eblregion).insert(square1)


    # Metal overlap
    metal1 = Polygon([
        Point(-W - 0.02 / dbu, -l/2),
        Point(-W + w + 0.02 / dbu, -l/2),
        Point(-W + w - 2 / dbu, -l/2 - 10 / dbu),
        Point(-W + w - 2 / dbu, -l/2 - 20 / dbu),
        Point(-W + w - 12 / dbu, -l/2 - 20 / dbu),
        Point(-W - 7 / dbu, -l/2 - 10 / dbu)
    ])
    metal2 = Polygon([
        Point(W + 0.02 / dbu, -l/2),
        Point(W - w - 0.02 / dbu, -l/2),
        Point(W - w + 2 / dbu, -l/2 - 10 / dbu),
        Point(W - w + 2 / dbu, -l/2 - 20 / dbu),
        Point(W - w + 12 / dbu, -l/2 - 20 / dbu),
        Point(W + 7 / dbu, -l/2 - 10 / dbu)
    ])
    shapes(LayerMetal).insert(metal1)
    shapes(LayerMetal).insert(metal2)

    # Pins
    pin1 = Path([Point(-W + w/2 - 4.5 / dbu, -l/2 - 10 / dbu + w),
                 Point(-W + w/2 - 4.5 / dbu, -w - l/2 - 10 / dbu)],
                w + 5 / dbu)
    shapes(LayerPinRecN).insert(pin1)
    shapes(LayerPinRecN).insert(Text("pin1", Trans(Trans.R270, -W + w/2 - 4.5 / dbu, -l/2 - 10 / dbu))).text_size = 0.4 / dbu

    pin2 = Path([Point(W - w/2 + 4.5 / dbu, -l/2 - 10 / dbu + w),
                 Point(W - w/2 + 4.5 / dbu, -w - l/2 - 10 / dbu)],
                w + 5 / dbu)
    shapes(LayerPinRecN).insert(pin2)
    shapes(LayerPinRecN).insert(Text("pin2", Trans(Trans.R270, W - w/2 + 4.5 / dbu, -l/2 - 10 / dbu))).text_size = 0.4 / dbu
    


    # DevRec
    if photonic_layer:
      pin3 = Path([Point(0, l/2 + 1 / dbu + 0.05 / dbu),
                 Point(0, -0.05 / dbu + l/2 + 1 / dbu)],
                  0.5 / dbu)
      shapes(LayerPinRecN).insert(pin3)
      shapes(LayerPinRecN).insert(Text("pin3", Trans(Trans.R270, 0, l/2 + 1 / dbu))).text_size = 0.4 / dbu

      devrec_box = [
          Point(-26 / dbu, -l/2 - 22 / dbu),
          Point(26 / dbu, -l/2 - 22 / dbu),
          Point(26 / dbu, l/2 + 1 / dbu),
          Point(-26 / dbu, l/2 + 1 / dbu),
      ]
    else:
          devrec_box = [
          Point(-W - 7 / dbu, -l/2 - 10 / dbu),
          Point(W + 7 / dbu, -l/2  - 10 / dbu),
          Point(W + 7 / dbu, l/2),
          Point(-W - 7 / dbu, l/2),
      ]

    shapes(LayerDevRecN).insert(Polygon(devrec_box))

    # Text
    t = Trans(Trans.R270, radius, l / 4)
    label = Text('NbTiNnanowire:w=%.3fu r=%.3fu l=%.3fu' % (self.w * 1000, self.radius * 1000, self.l), t)
    shapes(LayerDevRecN).insert(label).text_size = 0.5 / dbu

    layer_temp = self.layout.layer(LayerInfo(914, 0))
    shapes_temp = self.cell.shapes(layer_temp)
    ShapeProcessor().merge(self.layout, self.cell, LayerCladN, shapes_temp, True, 0, True, True)

    # Clear original LayerCladN and insert merged result back
    self.cell.shapes(LayerCladN).clear()
    ShapeProcessor().merge(self.layout, self.cell, layer_temp, self.cell.shapes(LayerCladN),True, 0, True, True)

    # Clean up temp layer
    self.cell.shapes(layer_temp).clear()
