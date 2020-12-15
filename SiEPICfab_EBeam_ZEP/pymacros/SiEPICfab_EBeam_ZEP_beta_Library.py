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

if 'SiEPICfab_EBeam_ZEP_beta_pcells' in locals():
    del SiEPICfab_EBeam_ZEP_beta_pcells
import SiEPICfab_EBeam_ZEP_beta_pcells


import sys
if int(sys.version[0]) > 2:
  from importlib import reload

class SiEPICfab_EBeam_ZEP_beta_Library(Library):
  """
  The library where we will put the PCells and GDS into 
  """

  def __init__(self):
  
    tech_name = 'SiEPICfab_EBeam_ZEP'
    library = 'SiEPICfab_EBeam_ZEP_beta'

    print("Initializing '%s' Library." % library)

    # Set the description
    self.description = "v0.0.1, Beta Components"

  
    # Import all the GDS files from the tech folder "gds"
    import os, fnmatch
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../fixed_beta")
    search_str = '*' + '.gds'
    for root, dirnames, filenames in os.walk(dir_path, followlinks=True):
        for filename in fnmatch.filter([f.lower() for f in filenames], search_str):
            file1=os.path.join(root, filename)
            print(" - reading %s" % file1 )
            self.layout().read(file1)
    
       
    # Create the PCell declarations
    for attr, value in SiEPICfab_EBeam_ZEP_beta_pcells.__dict__.items():
        if '__module__' in dir(value):
            try:
                if value.__module__.split('.')[0] == 'SiEPICfab_EBeam_ZEP_beta_pcells' and attr != 'cls':
                    print('Registered pcell: '+attr)
                    self.layout().register_pcell(attr, value())
            except:
                pass
    print(' done with pcells')
    # Register us the library with the technology name
    # If a library with that name already existed, it will be replaced then.
    self.register(library)

    if int(Application.instance().version().split('.')[1]) > 24:
      # KLayout v0.25 introduced technology variable:
      self.technology=tech_name

    self.layout().add_meta_info(LayoutMetaInfo("path",os.path.realpath(__file__)))
    self.layout().add_meta_info(LayoutMetaInfo("technology",tech_name))
 
# Instantiate and register the library
# SiEPICfab_EBeam_ZEP_beta_Library()