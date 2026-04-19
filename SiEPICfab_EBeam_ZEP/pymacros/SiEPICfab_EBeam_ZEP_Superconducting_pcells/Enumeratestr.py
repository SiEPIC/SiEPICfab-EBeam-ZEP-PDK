# Waveguide Bragg grating
# imported from SiEPIC_EBeam_PDK.  Model does not exist. Layout only.

from . import *
import pya
from pya import *
import math
class Enumeratestr(pya.PCellDeclarationHelper):
  def __init__(self):
    super(Enumeratestr, self).__init__()

    from SiEPIC.utils import get_technology_by_name
    self.technology_name = 'SiEPICfab_EBeam_ZEP'
    TECHNOLOGY = get_technology_by_name(self.technology_name)
    self.TECHNOLOGY = TECHNOLOGY

    # Override NbTiN to hardcoded 1/69
    self.param("line_width", self.TypeDouble, "Character line width (microns)", default=5)
    self.param("width", self.TypeDouble, "Character width (microns)", default=40)
    self.param("text", self.TypeString, "Text to display", default="HELLO-123")

    self.param("layer", self.TypeLayer, "Layer", default=LayerInfo(22, 0))

  def display_text_impl(self):
    # Provide a descriptive text for the cell
    return f"Text: {self.text}"

  def can_create_from_shape_impl(self):
    return False

  def produce_impl(self):
    """
    Generate the PCell output for a given string.
    """
    # Fetch the parameters
    ly = self.layout    
    dbu = ly.dbu
    
    LayerSi = ly.layer(self.layer)
        
    Ts = self.line_width / dbu
    Ws = self.width / dbu
    text = self.text.upper()  # Convert text to uppercase for uniformity

    # Segment Codes for A-Z, 1-9, and '-'
    segments = {"A": ["a", "b", "c", "g1", "f", "e"],
    "B": ["a", "b", "c", "d", "g1", "g2", "e", "f"],
    "C": ["a", "f", "e", "d"],
    "D": ["a", "b", "c", "d", "f", "e"],
    "E": ["a", "f", "e", "d", "g1"],
    "F": ["a", "f", "e", "g1"],
    "G": ["a", "f", "e", "d", "c", "g2"],
    "H": ["f", "b", "g1", "g2", "e", "c"],
    "I": ["a", "b", "c", "d"],
    "J": ["b", "c", "d"],
    "K": ["f", "e", "g1", "g2", "h", "k"],
    "L": ["f", "e", "d"],
    "M": ["c", "e","f", "b", "h", "i"],
    "N": ["f", "b", "h", "k"],
    "O": ["a", "b", "c", "d", "e", "f"],
    "P": ["a", "f", "g1", "b", "e"],
    "Q": ["a", "b", "c", "d", "e", "f", "k"],
    "R": ["a", "f", "g1", "b", "k", "e"],
    "S": ["a", "f", "g1", "c", "d"],
    "T": ["a", "b", "c"],
    "U": ["f", "b", "c", "d", "e"],
    "V": ["f", "b", "j", "k"],
    "W": ["f", "b", "h", "i", "j", "k"],
    "X": ["h", "i", "j", "k"],
    "Y": ["f", "b", "h", "k"],
    "Z": ["a", "g1", "g2", "d"],
}


    segment_definitions =  {
    "a": [[-Ws / 2, Ws / 2], [Ws / 2, Ws / 2], [Ws / 2, Ws / 2 - Ts], [-Ws / 2, Ws / 2 - Ts]],  # Top horizontal
    "b": [[Ws / 2, Ws / 2], [Ws / 2 + Ts, Ws / 2], [Ws / 2 + Ts, 0], [Ws / 2, 0]],  # Top-right vertical
    "c": [[Ws / 2, -Ws / 2], [Ws / 2 + Ts, -Ws / 2], [Ws / 2 + Ts, -Ws], [Ws / 2, -Ws]],  # Bottom-right vertical
    "d": [[-Ws / 2, -Ws], [Ws / 2, -Ws], [Ws / 2, -Ws - Ts], [-Ws / 2, -Ws - Ts]],  # Bottom horizontal
    "e": [[-Ws / 2 - Ts, -Ws], [-Ws / 2, -Ws], [-Ws / 2, -Ws / 2], [-Ws / 2 - Ts, -Ws / 2]],  # Bottom-left vertical
    "f": [[-Ws / 2 - Ts, Ws / 2], [-Ws / 2, Ws / 2], [-Ws / 2, 0], [-Ws / 2 - Ts, 0]],  # Top-left vertical
    "g1": [[-Ws / 2, Ts / 2], [Ws / 2, Ts / 2], [Ws / 2, -Ts / 2], [-Ws / 2, -Ts / 2]],  # Upper middle horizontal
    "g2": [[-Ws / 2, -Ws / 2 + Ts / 2], [Ws / 2, -Ws / 2 + Ts / 2], [Ws / 2, -Ws / 2 - Ts / 2], [-Ws / 2, -Ws / 2 - Ts / 2]],  # Lower middle horizontal
    # Top-left diagonal
    "h": [[-Ws / 2, Ws / 2], [0, 0], [-Ts / 2, 0], [-Ws / 2 + Ts, Ws / 2 - Ts]],

    # Top-right diagonal
    "i": [[Ws / 2, Ws / 2], [0, 0], [Ts / 2, 0], [Ws / 2 - Ts, Ws / 2 - Ts]],
    "j": [[-Ws / 2, -Ws / 2], [-Ts / 2, -Ws], [-Ws / 2, -Ws]],  # Lower-left diagonal
    "k": [[Ws / 2, -Ws / 2], [Ts / 2, -Ws], [Ws / 2, -Ws]],  # Lower-right diagonal
    "l": [[-Ws / 2, 0], [-Ws / 2 - Ts, 0], [-Ws / 2 - Ts, -Ws / 2], [-Ws / 2, -Ws / 2]],  # Middle-left vertical
    "m": [[Ws / 2, 0], [Ws / 2 + Ts, 0], [Ws / 2 + Ts, -Ws / 2], [Ws / 2, -Ws / 2]],  # Middle-right vertical
}






    si_region = pya.Region()
      
    for temp1, char in enumerate(text):  # Loop through the string
      if char not in segments:
          continue  # Skip characters that are not defined
    
      char_segments = segments[char]  # Get the active segments for this character
    
      for segment_name in char_segments:  # Loop through the active segments
        segment_coords = segment_definitions[segment_name]  # Get the polygon coordinates for this segment
    
        # Adjust the segment position for the current character
        xp = [(x + (temp1 - len(text) / 2) * Ws * 1.5) for x, y in segment_coords]
        yp = [y for x, y in segment_coords]

        # Create the polygon
        polygon = []
        for x, y in zip(xp, yp):
            polygon.append(pya.Point(x, y))
        
          # Insert the segment polygon into the region
        si_region.insert(pya.Polygon(polygon))
    
  # Insert the generated region into the layer
    self.cell.shapes(LayerSi).insert(si_region)
    
    