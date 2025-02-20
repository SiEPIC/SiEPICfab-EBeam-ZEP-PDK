
import pya
from pya import *

# Configure the export 
#  True: high and low resolution layers exported
#  False: high and low resolution layers merged into one high res layer
# 2020/12: process currently only uses high resolution
HighandLowRes = True

def boolean_layer_operations(topcell_in, flatten=False):

    from pya import Layout
    p = pya.AbsoluteProgress("SiEPICfab EBeam ZEP layer boolean operations")
    p.format_unit = topcell_in.layout().cells()+1
    
    # input
    layout_in = topcell_in.layout()
    flag_longcellnames = False
    
    # Create a new layout
    layout = Layout()
    topcell = layout.create_cell(topcell_in.name)

    # Create new layers for the inverted layout
    layer_etch_high = layout.layer(pya.LayerInfo(100, 0))
    layer_etch_low = layout.layer(pya.LayerInfo(101, 0))
    layer_core=layout.layer(pya.LayerInfo(1, 0))
    layer_clad = layout.layer(pya.LayerInfo(1, 2))
    layer_temp = layout.layer(pya.LayerInfo(1, 455))
    layer_temp2 = layout.layer(pya.LayerInfo(1, 456))

    # copy layout
    topcell.copy_tree(topcell_in)    
    p.inc
    
    # flatten the layout
    if flatten:
        topcell.flatten(-1, True)
    
    # scan through all cells
    for i in range(0,layout.cells()):
        if not layout.is_valid_cell_index(i):
            # cell does not exist, skip
            continue
                        
        cell = layout.cell(i)

        print(" - cell: %s" % cell.name)
        if len(cell.name)>64:
            # mark this layout as containing long cells names, to deal with during save
            flag_longcellnames = True
            print("   - WARNING: too many characters in cell name")

        # shape containers            
        shapes_etch_high = cell.shapes(layer_etch_high)
        shapes_etch_low = cell.shapes(layer_etch_low)
        shapes_core = cell.shapes(layer_core)
        shapes_clad = cell.shapes(layer_clad)
        shapes_temp = cell.shapes(layer_temp)
        shapes_temp2 = cell.shapes(layer_temp2)

        # NOT draw with clad
        pya.ShapeProcessor().boolean(
            layout,cell,layer_core,
            layout,cell,layer_clad,
            shapes_temp2,pya.EdgeProcessor.ModeBNotA,False,True,True)
        shapes_core.clear()   
        shapes_clad.clear()
        
        if not HighandLowRes:
            # merge low etch layer, into high layer
            pya.ShapeProcessor().boolean(
                layout,cell,layer_etch_high,
                layout,cell,layer_etch_low,
                shapes_temp,pya.EdgeProcessor.ModeOr,False,True,True)
            shapes_etch_high.clear()
            shapes_etch_low.clear()
                        
            # OR etch with calculated etch
            pya.ShapeProcessor().boolean(
                layout,cell,layer_temp,
                layout,cell,layer_temp2,
                shapes_etch_high,pya.EdgeProcessor.ModeOr,False,True,True)
        else:
            # OR etch with calculated etch
            pya.ShapeProcessor().boolean(
                layout,cell,layer_etch_high,
                layout,cell,layer_temp2,
                shapes_etch_high,pya.EdgeProcessor.ModeOr,False,True,True)

        shapes_temp.clear()
        shapes_temp2.clear()
        
        p.inc
        
    p.destroy

    return layout, flag_longcellnames



def export_for_fabrication(flatten=False, replace_IP=False):
 
    extra = "static" # what to append at the end of the filename.
  
    import SiEPIC
    from SiEPIC import _globals
    from SiEPIC.utils import get_layout_variables
    TECHNOLOGY, lv, ly, topcell = get_layout_variables()
    import os

    # Save the layout prior to exporting, if there are changes.
    mw = pya.Application.instance().main_window()
    if mw.manager().has_undo():
        mw.cm_save()
    layout_filename = mw.current_view().active_cellview().filename()

    if len(layout_filename) == 0:
        raise Exception("Please save your layout before exporting.")
   
    # check if the currently selected cell is a top cell
    if topcell in ly.top_cells():
#    if topcell.name in [n.name for n in ly.top_cells()]:
        if len(ly.top_cells()) > 1:
            print(' - Warning: You may only have one top cell in your hierarchy. Clean up using SiEPIC > Layout > Delete Extra Top Cells.')
            print(' - Warning: Exporting top cell: %s' % topcell.name)
    else:
        if len(ly.top_cells()) == 1:
            # choose the single top cell for export
            topcell = ly.top_cells()[0]
        else:
            raise Exception("You may only have one top cell in your hierarchy. \nClean up using SiEPIC > Layout > Delete Extra Top Cells. \nOr, select the desired top cell using Show as New Top.")
        
    if replace_IP:
        ly.technology_name='SiEPICfab_EBeam_ZEP'
        cell_list = [
        #['GC_1550_220_Blackbox', 'GC_1550_te_220', 'SiEPICfab_EBeam_ZEP_UBC'],
        #['ebeam_gc_te1550', 'GC_1550_te_220', 'SiEPICfab_EBeam_ZEP_UBC'],
        ['y_splitter_1310', 'drp_o_y_splitter', 'SiEPICfab_EBeam_ZEP_UBC'],
        #['GC_1270_te_220_Blackbox','GC_1270_te_220', 'SiEPICfab_EBeam_ZEP_UBC'], 
#        ['GC_1290_te_220_Blackbox','GC_1290_te_220', 'SiEPICfab_EBeam_ZEP_UBC'], 
        #['GC_1310_te_220_Blackbox','GC_1310_te_220', 'SiEPICfab_EBeam_ZEP_UBC'], 
        ['GC_1550_te_220','ebeam_GC_Air_te1550', 'SiEPICfab_EBeam_ZEP_UBC'], 
        ['ebeam_GC_Air_te1550_BB','ebeam_GC_Air_te1550', 'SiEPICfab_EBeam_ZEP_UBC'], 
        ['ebeam_GC_Air_te1310_BB','ebeam_GC_Air_te1310', 'SiEPICfab_EBeam_ZEP_UBC'], 
        ['GC_Air_te1310_BB','ebeam_GC_Air_te1310', 'SiEPICfab_EBeam_ZEP_UBC'], 
        ['GC_TE_1550_8degOxide_BB','ebeam_GC_Air_te1550', 'SiEPICfab_EBeam_ZEP_UBC'], 
        #['ebeam_GC_Air_tm1310_BB','GC_1310_te_220', 'SiEPICfab_EBeam_ZEP_UBC'], 
        ['laser_1310nm_DFB_BB','laser_1270nm_DFB', 'SiEPICfab_EBeam_ZEP_UBC'], 
        ]
        from SiEPIC.scripts import replace_cell
        text_out = ''
        for i in range(len(cell_list)):
            text_out = replace_cell(ly, cell_x_name=cell_list[i][0], cell_y_name=cell_list[i][1], cell_y_library=cell_list[i][2], Exact = False)

    ly, flag_longcellnames = boolean_layer_operations(topcell, flatten=flatten)


    # Save the layout, without PCell info, for fabrication
    save_options = pya.SaveLayoutOptions()

    # remove $$$CONTEXT_INFO$$$ PCells
    save_options.write_context_info=False  

    # file format
    if flag_longcellnames:
        # GDS save option allows for a max cell name
        save_options.format='GDS2'
        save_options.gds2_no_zero_length_paths = True
        save_options.gds2_max_cellname_length = 64
        save_options.gds2_write_cell_properties = False
        save_options.gds2_write_file_properties = False
    else:
        save_options.format='OASIS' # smaller file size
        save_options.oasis_compression_level = 10
        save_options.oasis_permissive = True
        save_options.oasis_recompress = True
        save_options.oasis_substitution_char = "-"

    if SiEPIC.__version__ < '0.3.73':
        pya.MessageBox.warning("Errors", "Please upgrade to SiEPIC-Tools version 0.3.73 or greater.", pya.MessageBox.Ok)
    else:
        ly.cell_character_replacement(forbidden_cell_characters = '=', replacement_cell_character = '_')

    # only export the layers that will be fabricated
    save_options.add_layer(ly.layer(LayerInfo(100,0)), LayerInfo())# Si etch high res
    save_options.add_layer(ly.layer(LayerInfo(101,0)), LayerInfo())# Si etch low res
    save_options.add_layer(ly.layer(LayerInfo(11,0)), LayerInfo(12,0)) # M1
    save_options.add_layer(ly.layer(LayerInfo(12,0)), LayerInfo()) # M2
    save_options.add_layer(ly.layer(LayerInfo(99,0)), LayerInfo()) # Floorplan
    save_options.add_layer(ly.layer(LayerInfo(8100,0)), LayerInfo()) # EBL regions
    save_options.add_layer(ly.layer(LayerInfo(10,0)), LayerInfo()) # Text
    save_options.add_layer(ly.layer(LayerInfo(201,0)), LayerInfo())# Deep trench etch

    # filename
    file_out = os.path.join(os.path.dirname(layout_filename), os.path.splitext(os.path.basename(layout_filename))[0]+'_%s.'%extra+save_options.format[0:3].lower())
    print("saving output %s: %s" % (save_options.format, file_out) )

    try:
        ly.write(file_out,save_options)
    except:
        raise Exception("Problem exporting your layout.")
 
    pya.MessageBox.warning("Success.", "Layout exported successfully: \n%s" %file_out, pya.MessageBox.Ok)
