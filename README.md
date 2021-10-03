# SiEPICfab-EBeam-ZEP-PDK
SiEPIC Program EBeam PDK for the ZEP process

## Technical summary:
- SOI wafer, 220 nm silicon
- Single full etch, using a positive resist (ZEP)
- No cladding

## Layer table
| Name            | Layer/datatype | Description                                                                          |
|-----------------|----------------|--------------------------------------------------------------------------------------|
| Si_core         | 1/0            |             Layer to draw silicon waveguides; will be XORed with Si_clad.            |
| Si_clad         | 1/2            |         Layer to draw the extent of the Si etch, including cladding and core.        |
| Si_etch_highres | 100/0          | High Resolution Layer to draw fully etched trenches, but use SLS/Shape PEC. (trench) |
| Si_etch_lowres  | 101/0          | Low Resolution Layer to draw fully etched trenches but use no-SLS or PEC. (trench)   |
| Floorplan       | 99/0           |                             Marks the layout design area.                            |
| text            | 10/0           | Text labels for automated measurements.                                              |
| DevRec          | 68/0           |                           Device recognition layer for DRC.                          |
| PinRec          | 1/10           | Port/pins recognition layer for snapping and connectivity checks.                    |
| Waveguide       | 1/99           | Virtual layer, guiding shape for waveguide, used for length calculation              |
| SEM             | 200/0          | Requests for SEM images. Rectangles in a 4:3 aspect.                                 |
| EBL-Regions     | 8100/0         | EBL Litho Manual Write Field Regions                                                 |

## People
- Fabrication performed at UBC by Kashif Awan
- PDK support provided by Jaspreet Jhoja

## Run schedule
- SiEPICfab process development runs, typically bi-weekly or monthly
- Contact Steven Gou for scheduling

## PDK installation instructions:

### Software - KLayout, SiEPIC-Tools
- Install KLayout version 0.26 or greater: http://www.klayout.de/build.html
- Install SiEPIC-Tools versus 0.3.71 or higher, using the Package Manager [(instructions)](https://github.com/SiEPIC/SiEPIC-Tools/wiki/Installation)

## PDK Installation via GitHub Desktop (most suitable for developers):

- Install GitHub Desktop, https://desktop.github.com
- Clone this repostory using GitHub Desktop.  Do this by clicking on the green "Code" button, then "Open with GitHub Desktop"
    - Example below assumes it is installed in your Documents folder. 
- There are different branches, "main" and "experimental". Choose the branch in GitHub Desktop via the "Current Branch" button
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

## Submission

- Design Rule check: please check using both:
  - KLayout SiEPIC > Verification > Design Rule Check (DRC) - SiEPICfab-ZEP
  - KLayout SiEPIC > Verification > Functional Layout Check
  - All the design rules should be considered as "warnings", and you do not need to obtain Waivers for violations
- File format: GDS or OASIS.  Use the KLayout SiEPIC > Export for SiEPICfab-ZEP fabrication
   - this script performs the required layer boolean operations and basic clean-up

### For SiEPICfab members:
 - Please fill in the form here: https://docs.google.com/forms/d/e/1FAIpQLSeFrlBozNWQ5TLEB5X2LdBlOMgfqfcz9K8cZBww6_-Xg-Zsag/viewform
   - choose "Process Development"
 - Designs should be uploaded to the UBC Nextcloud server (links provided in the Google form)

## Contributions to the PDK
- Please make contributions, preferably using a Pull request.

