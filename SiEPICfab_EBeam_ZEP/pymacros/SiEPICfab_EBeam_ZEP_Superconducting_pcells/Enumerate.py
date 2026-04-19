# Waveguide Bragg grating
# imported from SiEPIC_EBeam_PDK.  Model does not exist. Layout only.

from . import *
import pya
from pya import *
import numpy as np
class Enumerate(pya.PCellDeclarationHelper):
  def __init__(self):
    super(Enumerate, self).__init__()

    from SiEPIC.utils import get_technology_by_name
    self.technology_name = 'SiEPICfab_EBeam_ZEP'
    TECHNOLOGY = get_technology_by_name(self.technology_name)
    self.TECHNOLOGY = TECHNOLOGY

    # declare the parameters
    self.param("align_length", self.TypeDouble, "Alignment mark length (microns)", default = 10)
    self.param("align_width", self.TypeDouble, "Alignment mark width (microns)", default = 1)
    #    self.param("rect_length", self.TypeDouble, "Alignment mark corner length (microns)", default = 3)
    self.param("marklayer", self.TypeLayer, "Mark Layer", default = LayerInfo(11, 0))
    #    self.param("pinrec", self.TypeLayer, "PinRec Layer", default = LayerInfo(69, 0))
    self.param("devrec", self.TypeLayer, "DevRec Layer", default = LayerInfo(68, 0))
    
  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "Alignment_mark _length-%.3f_width-%.3f" % (self.align_length, self.align_width)
  
  def can_create_from_shape_impl(self):
    return False


  def produce_impl(self):
    """
    coerce parameters (make consistent)
    """

    # fetch the parameters
    ly = self.layout    
    dbu = ly.dbu
    
    LayerMark = ly.layer(self.marklayer)
#    LayerPinRecN = ly.layer(self.pinrec)
    LayerDevRecN = ly.layer(self.devrec)
        
    L = self.align_length/dbu
    W = self.align_width/dbu
#    L2 = self.rect_length/dbu

    align_vertical = pya.Region()
    align_horizontal = pya.Region()
    rect_vertical = pya.Region()
    rect_horizontal = pya.Region()
    
    # central cross
    vertical_poly =pya.Polygon([pya.Point(-W/2,L/2), pya.Point(-W/2,-L/2), pya.Point(W/2,-L/2), pya.Point(W/2,L/2)])
    horizontal_poly = pya.Polygon([pya.Point(-L/2,W/2), pya.Point(-L/2,-W/2), pya.Point(L/2,-W/2), pya.Point(L/2,W/2)])
    align_vertical.insert(vertical_poly)
    align_horizontal.insert(horizontal_poly)
 

    Mark_region = align_vertical | align_horizontal
       
    Mark_region.insert((rect_vertical|rect_horizontal))
        
    self.cell.shapes(LayerMark).insert(Mark_region)

    return "align_mark"     

############################################################

class Enumerate(pya.PCellDeclarationHelper):
  """
  The PCell declaration for one alignment mark.
  """

  def __init__(self):

    # Important: initialize the super class
    super(Enumerate, self).__init__()
    # declare the parameters
    self.param("line_width", self.TypeDouble, "Digit line width (microns)", default = 5)
    self.param("width", self.TypeDouble, "Digit width (microns)", default = 40)
    self.param("text", self.TypeString, "String to display (e.g., 1-23-456)", default="123")

    self.param("layer", self.TypeLayer, "Layer", default = LayerInfo(13, 0))
    
  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return "Enumerate "
  
  def can_create_from_shape_impl(self):
    return False


  def produce_impl(self):
    """
    coerce parameters (make consistent)
    """

    # fetch the parameters
    ly = self.layout    
    dbu = ly.dbu
    
    LayerSi = ly.layer(self.layer)
        
    Ts = self.line_width/dbu
    Ws= self.width/dbu
    text = self.text

    # Segment Codes:
    S = {
            "0": [1, 1, 1, 1, 1, 1, 0],  # 0
            "1": [0, 0, 0, 1, 1, 0, 0],  # 1
            "2": [1, 0, 1, 1, 0, 1, 1],  # 2
            "3": [0, 0, 1, 1, 1, 1, 1],  # 3
            "4": [0, 1, 0, 1, 1, 0, 1],  # 4
            "5": [0, 1, 1, 0, 1, 1, 1],  # 5
            "6": [1, 1, 1, 0, 1, 1, 1],  # 6
            "7": [0, 0, 1, 1, 1, 0, 0],  # 7
            "8": [1, 1, 1, 1, 1, 1, 1],  # 8
            "9": [0, 1, 1, 1, 1, 1, 1],  # 9
            "-": [0, 0, 0, 0, 0, 0, 1],  # Dash
            " ": [0, 0, 0, 0, 0, 0, 0],  # Space
        }

    
    Shv = ['v', 'v', 'h', 'v', 'v', 'h', 'h'] # Vertical/Horizontal Segment
    Xn = np.array([-1, -1, 0, 1, 1, 0, 0])*1.0/2*Ws # Segments positions
    Yn = np.array([-1, 1, 2, 1, -1, -2, 0])*1.0/2*Ws    

# Split text into lines without breaking dashes and numbers
    groups = text.split('-')
    lines = []
    current_line = ""

    for group in groups:
        # Check if adding the next group exceeds the 10-character limit
        if len(current_line) + len(group) + (1 if current_line else 0) > 12:
            lines.append(current_line)  # Start a new line
            current_line = group  # Start with the new group
        else:
            # Add the group to the current line
            if current_line:
                current_line += "-"  # Add a dash before the group
            current_line += group

    if current_line:
        lines.append(current_line)  # Append the remaining line

    # Create a region to insert the segments
    si_region = pya.Region()

    for line_idx, line in enumerate(lines):  # Process each line
        for temp1, char in enumerate(line):  # Loop through the characters in the line
            if char not in S:
                continue  # Skip unsupported characters

            char_segments = S[char]  # Get the active segments for this character
            for temp2 in range(0, 7):  # Loop through the 7 segments
                if char_segments[temp2] != 0:
                    segment = []
                    vertical_offset = -line_idx * (2 * Ws + 2 * Ts)  # Adjust for vertical split
                    if Shv[temp2] == 'h':  # Horizontal Segment
                        xp = Xn[temp2] + [
                            -(Ws / 2 - Ts) - Ts / 2, -(Ws / 2 - Ts), (Ws / 2 - Ts), (Ws / 2 - Ts) + Ts / 2,
                            (Ws / 2 - Ts), -(Ws / 2 - Ts), -(Ws / 2 - Ts) - Ts / 2
                        ] + (temp1 - len(line) / 2) * Ws * 1.5
                        yp = Yn[temp2] + [0, -Ts / 2, -Ts / 2, 0, Ts / 2, Ts / 2, 0] + vertical_offset
                    else:  # Vertical Segment
                        xp = Xn[temp2] + [0, Ts / 2, Ts / 2, 0, -Ts / 2, -Ts / 2, 0] + (
                            (temp1 - len(line) / 2) * Ws * 1.5
                        )
                        yp = Yn[temp2] + [
                            -(Ws / 2 - Ts) - Ts / 2, -(Ws / 2 - Ts), (Ws / 2 - Ts),
                            (Ws / 2 - Ts) + Ts / 2, (Ws / 2 - Ts), -(Ws / 2 - Ts),
                            -(Ws / 2 - Ts) - Ts / 2
                        ] + vertical_offset

                    for temp3 in range(0, 7):  # Create a polygon for the segment
                        segment.append(pya.Point(xp[temp3], yp[temp3]))

                    si_region.insert(pya.Polygon(segment))

    # Insert the region into the layout
    self.cell.shapes(LayerSi).insert(si_region)

