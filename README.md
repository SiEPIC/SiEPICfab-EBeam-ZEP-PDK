# SiEPICfab-EBeam-ZEP-PDK
SiEPIC Program EBeam PDK for the ZEP process

## Technical summary:
- SOI wafer, 220 nm silicon
- Baseline process:
  - Single full etch, using a positive resist (ZEP)
  - No cladding
- Optional process modules:
  - Shuksan laser integration (deep trench, laser attach, photonic wire bonds)
  - Metals
  - Oxide release etch for NEMS devices
- [Process documentation, including process bias] (https://docs.google.com/document/d/1HpU0Z95oETRH_fx-z4YNDfZ5-b3SPxWYZX6zVMYroiM/edit?usp=sharing)

### Wafer details:
- 200mm 
- Top Silicon:
  - CZ grown P type Boron doped
  - 30-60 ohm cm. (approx 5e14 cm^-3, see https://www.pvlighthouse.com.au/resistivity)
  - 110 orientation
  - Notched within 1 degree
  - 220 nm thick+-12.5nm, all measured points, 5mm edge exclusion
- BOX: 
  - 3500 nm+-150nm all points, 5mm edge exclusion
- Handle:
  - CZ, P type Boron doped
  - 500-1000 ohm cm
  - 100 orientation
  - 725 um thick +-15 um
  - Backside etched with oxide
  - Max 50 um warp
 

## Layer table
| Name            | Layer/datatype | Description                                                                          |
|-----------------|----------------|--------------------------------------------------------------------------------------|
| Si_core         | 1/0            |             Layer to draw silicon waveguides; will be XORed with Si_clad.            |
| Si_clad         | 1/2            |         Layer to draw the extent of the Si etch, including cladding and core.        |
| Si_etch_highres | 100/0          | High Resolution Layer to draw fully etched trenches, but use SLS/Shape PEC. (trench) |
| Si_etch_lowres  | 101/0          | Low Resolution Layer to draw fully etched trenches but use no-SLS or PEC. (trench)   |
| M1              | 11/0           | Layer to draw metal routing, heaters, etc  				          |
| DeepTrench	  | 201/0          | Layer to define deep trench etch regions. For edge couplers			  |
| Floorplan       | 99/0           |                             Marks the layout design area.                            |
| text            | 10/0           | Text labels for automated measurements.                                              |
| DevRec          | 68/0           |                           Device recognition layer for DRC.                          |
| PinRec          | 1/10           | Port/pins recognition layer for snapping and connectivity checks.                    |
| Waveguide       | 1/99           | Virtual layer, guiding shape for waveguide, used for length calculation              |
| SEM             | 200/0          | Requests for SEM images. Rectangles in a 4:3 aspect.                                 |
| EBL-Regions     | 8100/0         | EBL Litho Manual Write Field Regions                                                 |

### EBL Write Field Regions
- layer “EBL-Regions”: Designer draws a rectangle to designate a write field. Maximum size of 1x1 mm. Everything inside is written in one EBL field. 
- Designer chooses their own fields to avoid field stitching boundaries, or to choose where the boundaries are placed
- Can have adjacent fields touching. Exported in order so that they are written as a group, which reduces stitching errors due to machine drift
- Run DRC check to make sure the EBL regions are defined correctly
- SiEPIC > "Export EBL Write Field Regions" - Script that exports EBL regions. Beamer will import and use for manual field placement. 

## People
- Fabrication performed at UBC

## Run schedule
- SiEPICfab process development runs, typically monthly
- Contact Serge Khorev for scheduling

# PDK installation instructions:

## Software - KLayout, SiEPIC-Tools
- Install KLayout version 0.27 or greater (latest version): http://www.klayout.de/build.html
- Install SiEPIC-Tools versus 0.3.71 or higher (latest version), using the Package Manager [(instructions)](https://github.com/SiEPIC/SiEPIC-Tools/wiki/Installation)

## PDK Installation via GitHub Desktop (easiest way to receive updates):

- Install GitHub Desktop, https://desktop.github.com  (works on Windows, Mac, Ubuntu)
- Clone this repostory using GitHub Desktop.  Do this by clicking on the green "Code" button, then "Open with GitHub Desktop"
    - Example below assumes it is installed in your Documents folder. 
- There are different branches, "main" and "experimental". Choose the branch in GitHub Desktop via the "Default Branch" button
- Start KLayout:
	* Menu Tools > Manage Technologies
	* In the window on the left (Technologies), right click, then Import Technology
	* Navigate to your Documents / GitHub folder and select GitHub / SiEPICfab-EBeam-ZEP-PDK, and find the .lyt file, then OK.
	* Create a new layout, menu File > New Layout, Technology = SiEPICfab-EBeam-ZEP
	   - you should see the layer table (corresponding to the table detaileda above), and the SiEPIC menu
- If that doesn't work, close KLayout, and try this:
  - Create a symbolic link from the repo PDK folder into your KLayout tech folder. If the tech folder does not exist, create it, ensuring the name of the folder is "tech". 
 
   - On Mac:

			$ mkdir ~/.klayout/tech
			$ ln -s ~/Documents/GitHub/SiEPICfab-EBeam-ZEP-PDK/SiEPICfab_EBeam_ZEP ~/.klayout/tech
			
   - On Windows:
   			
			$ cd C:\Users\<username>\KLayout\tech
			$ mklink /J SiEPICfab_EBeam_ZEP "C:\Users\<username>\Documents\GitHub\SiEPICfab-EBeam-ZEP-PDK\SiEPICfab_EBeam_ZEP"
			
 - Start KLayout, and create a new layout choosing Technology = SiEPICfab_EBeam_ZEP
   - you should see the layer table, and the SiEPIC menu
   

## PDK Updates:
 - subscribe to commits and release updates using the "Watch" button, https://github.com/SiEPIC/SiEPICfab-EBeam-ZEP-PDK
 - use GitHub Desktop to refresh the PDK ("Fetch origin"), then restart KLayout

## PDK Support:

- If you encounter problems, notice errors or omissions, or have suggestions, please post them here: [new Issue](https://github.com/siepic/SiEPICfab-EBeam-ZEP-PDK/issues). You may copy and paste a screenshot into the Issue.

## Waveguides:

- Draw a Path on the layer "Waveguide"
- menu SiEPIC > Waveguides > Path to Waveguides ("W"), choose one of the waveguide types

## Library:
- The SiEPICfab_EBeam_ZEP library contains true geometry fixed cells including a 50/50 splitter (ebeam_bdc_te1550), y-branch (ebeam_y_1550), and terminator. 
- The SiEPICfab_EBeam_ZEP library contains hidden geometry (black box) fixed cells: GC_1550_220_Blackbox; these will be replaced prior to fabrication
- The SiEPICfab_EBeam_ZEP library contains parameterized cells including Waveguide and taper


# Submission

- Design Rule check: please check using both:
  - KLayout SiEPIC > Verification > Design Rule Check (DRC) - SiEPICfab-ZEP
  - KLayout SiEPIC > Verification > Functional Layout Check
  - All the design rules should be considered as "warnings", and you do not need to obtain Waivers for violations
- File format: GDS or OASIS.  Use the KLayout SiEPIC > Export for SiEPICfab-ZEP fabrication
   - this script performs the required layer boolean operations and basic clean-up

## For SiEPICfab members:
 - Please fill in the form here: https://docs.google.com/forms/d/e/1FAIpQLSeFrlBozNWQ5TLEB5X2LdBlOMgfqfcz9K8cZBww6_-Xg-Zsag/viewform
   - choose "Process Development"
 - Designs should be uploaded to the UBC Nextcloud server (links provided in the Google form)

# Contributions to the PDK
- Please make contributions, preferably using a Pull request.

