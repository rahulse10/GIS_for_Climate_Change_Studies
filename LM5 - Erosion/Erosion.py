# Import system modules
import arcpy
from arcpy import env
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

## A result folder where the output of the MFD FlowDir is stored - the folder needs to exist before running the script
## I have made a new empty ArcGIS Pro project called "Erosion" and have let the system generate a default gdf and a default folder
## Below here, I set the path to the default folder
Res_fld = "C:/Fag/Geog3527_GIS4CCS/Exercises/Ex5_Erosion/Erosion/"
## Set up the path to the workspace where you have data for "your" watershed - this could be the default gdb.
## Data you need include:
## - a hydro-corrected DEM (here: DEM_fill) - copy one from your previous exercises into a gdb you create for this exercise
## - a feature class representing the part of "your" watershed that is on land (here: MyWatershed_Land)
## - a feature class representing the sediments (here: fcSediments)
## - a look-up table with erosion prone coding
env.workspace = "C:/Fag/Geog3527_GIS4CCS/Exercises/Ex5_Erosion/Erosion/Erosion.gdb"

## Set Geoprocessing environments
arcpy.env.snapRaster = "DEM_fill"
arcpy.env.extent = "DEM_fill"

print ("Preparing slope ...")
arcpy.Slope_3d("DEM_fill", "rSlope", "DEGREE")
print ("Reclassify - 10 degrees slopes = 1")
arcpy.gp.Reclassify_sa("rSlope", "Value", "0 10 NODATA;10 90 1", "rSlope10", "DATA")

print ("Prepare the Flow Accumulation Raster ...")
print ("    Generate a MFD  raster")
FlowDirMFD = Res_fld + "FlowDirMFD.crf"
arcpy.gp.FlowDirection_sa("DEM_fill", FlowDirMFD, "NORMAL", "", "MFD")
print ("    Generate Flow Accumulation Raster")
arcpy.gp.FlowAccumulation_sa(FlowDirMFD, "rFlowAccMFD", "", "INTEGER", "MFD")
print ("    Reclassify the FlowAcc raster to highlight surface flow")
arcpy.gp.Reclassify_sa("rFlowAccMFD", "Value", "-2147483648 200 NODATA;200 2009479709 1", "rFlowAcc200MFD", "DATA")

print ("Preparing sediment layer")
print ("    Clip sediment feature class to study area...")
arcpy.Clip_analysis("fcSediments", "MyWatershed_Land", "fcSediments_Clip")
print ("    Join field with erosion prone ranking")
arcpy.JoinField_management("fcSediments_Clip", "jordart", "LookUpTable4Erosion", "Kode", ["Kategori"])
## seperate the sediments most prone for erosion (kategori = 3) - change the expression to make selection for also lower values erodeness kategories 
arcpy.analysis.Select("fcSediments_Clip", "fcSediments_Cat3", "Kategori > 2")
arcpy.PolygonToRaster_conversion("fcSediments_Cat3", "Kategori", "rSediments_temp", "MAXIMUM_AREA", "", 1.0)
arcpy.gp.Reclassify_sa("rSediments_temp", "Value", "0 NODATA;3 1", "rSediments_Cat3", "DATA")

print ("Preparing erosion layer")
print ("    Identify erosion prone areas")
arcpy.gp.Times_sa("rSediments_Cat3", "rFlowAcc200MFD", "rTemp1")
arcpy.gp.Times_sa("rTemp1", "rSlope10", "rTemp2")
arcpy.gp.Reclassify_sa("rTemp2", "Value", "0 NODATA;1 1", "rErosjon_Cat3", "DATA")
print ("    Convert erosion exposed areas to polygon feature")
arcpy.RasterToPolygon_conversion("rErosjon_Cat3", "fcErosjon_tmp", "NO_SIMPLIFY", "Value", "SINGLE_OUTER_PART", "")
print ("    Remove all erosion-polygon that only occupy one pixel's area")
arcpy.analysis.Select("fcErosjon_tmp", "fcErosjon_Cat3", "Shape_Area > 1")
