"""
This file is part of the SiEPICfab_EBeam_ZEP_PDK
by Jaspreet Jhoja, Lukas Chrostowski (c) 2020

"""
import math
from SiEPIC.utils import get_technology, get_technology_by_name

# Import KLayout Python API methods:
# Box, Point, Polygon, Text, Trans, LayerInfo, etc
import pya
from pya import *

if 'SiEPICfab_EBeam_ZEP_pcells' in locals():
    del SiEPICfab_EBeam_ZEP_pcells
import SiEPICfab_EBeam_ZEP_pcells


import sys
if int(sys.version[0]) > 2:
  from importlib import reload
# pcells_EBeam = reload(pcells_EBeam)

class SiEPICfab_EBeam_ZEP_Library(Library):
  """
  The library where we will put the PCells and GDS into 
  """

  def __init__(self):
  
    tech_name = 'SiEPICfab_EBeam_ZEP'
    library = 'SiEPICfab_EBeam_ZEP'

    print("Initializing '%s' Library." % library)

    # Set the description
# windows only allows for a fixed width, short description 
    self.description = ""
# OSX does a resizing:
    self.description = "v0.0.1, Beta Fixed Components"

  
    # Import all the GDS files from the tech folder "gds"
    from pathlib import Path
    dir_path = Path(__file__).parent/ "SiEPICfab_EBeam_ZEP_beta_fixed"
    for file1 in dir_path.rglob('*.gds'):
        file1 = file1.as_posix()
        print(" - reading %s" % file1 )
        self.layout().read(file1)    
       
    # Create the PCell declarations
    for attr, value in SiEPICfab_EBeam_ZEP_pcells.__dict__.items():
        if '__module__' in dir(value):
            try:
                if value.__module__.split('.')[0] == 'SiEPICfab_EBeam_ZEP_pcells' and attr != 'cls':
                    print('Registered pcell: '+attr)
                    self.layout().register_pcell(attr, value())
            except:
                pass
    print(' done with SiEPICfab_EBeam_ZEP_pcells')
    # Register us the library with the technology name
    # If a library with that name already existed, it will be replaced then.
    self.register(library)

    if int(Application.instance().version().split('.')[1]) > 24:
      # KLayout v0.25 introduced technology variable:
      self.technology=tech_name
      
    self.layout().add_meta_info(LayoutMetaInfo("path",str(Path(__file__))))
    self.layout().add_meta_info(LayoutMetaInfo("technology",tech_name))
 
# Instantiate and register the library
SiEPICfab_EBeam_ZEP_Library()