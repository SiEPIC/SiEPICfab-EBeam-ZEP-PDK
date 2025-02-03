

# Installing the PDK in developer mode
- Allows for editing the files, including Python layout cells, and Lumerical compact models
## KLayout installation
- Fork a copy of the repository
- Use GitHub Desktop to clone it
- Install it using Import Technology, pointing to the GitHub folder
## Lumerical installation
- Install using the SiEPIC menu > Simulations, Circuit > Install Lumerical CML. This installs it in the Design Kits folder
- Create a symbolic link to the Custom folder, similar to [these instructions](https://github.com/SiEPIC/SiEPIC_EBeam_PDK/wiki/Adding-components-and-models-to-the-PDK#install-the-cml-in-interconnect-as-a-custom-library).
  - mklink /D %userprofile%\AppData\Roaming\Custom\SiEPICfab_EBeam_ZEP %userprofile%\Documents\GitHub\SiEPICfab-EBeam-ZEP-PDK\siepicfab_ebeam_zep\CML\SiEPICfab-EBeam-ZEP

