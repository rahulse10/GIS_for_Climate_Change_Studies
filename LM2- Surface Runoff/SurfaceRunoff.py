# -*- coding: cp1252 -*-
# Import system modules
import arcpy
from arcpy import env

arcpy.CheckOutExtension("Spatial")

## Set Geoprocessing environments
arcpy.env.overwriteOutput = True
env.workspace =  "C:/Fag/Geog3527_GIS4CCS/Exercises/Ex2_SurfaceRunOff/Data/Ex2 Pluvial Flooding.gdb"
arcpy.env.snapRaster = "MyDEM5"
arcpy.env.extent = "MyDEM5"
print ("Make a hydro-corrected dem")
arcpy.gp.Fill_sa("MyDEM5", "dem_hydro")
print ("Generate a D8 directional raster")
arcpy.gp.FlowDirection_sa("dem_hydro", "FlowDir", "NORMAL", "", "D8")
print ("Generate Flow Accumulation Raster")
arcpy.gp.FlowAccumulation_sa("FlowDir", "FlowAcc", "", "INTEGER", "D8")
print ("Reclassify the FlowAcc raster to highlight surface flow") 
arcpy.gp.Reclassify_sa("FlowAcc", "Value", "-2147483648 10000 NODATA;10000 2009479709 1", "FlowAcc10", "DATA")
arcpy.gp.StreamToFeature_sa("FlowAcc10", "FlowDir", "fcFlowLine", "NO_SIMPLIFY")
print ("Remove parts of the flow lines that is located in the fjord ...")
arcpy.Clip_analysis("fcFlowLine", "Bekksneset_Land", "fcFlowLine2")

