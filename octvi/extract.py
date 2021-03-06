## set up logging
import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

## import modules
import octvi.exceptions, octvi.array, gdal
from gdalnumeric import *
import numpy as np


def getDatasetNames(stack_path:str) -> list:
	"""
	Returns list of all subdataset names, in format
	suitable for passing to other functions' 
	'dataset_name' argument
	"""

	## parsing arguments
	ext = os.path.splitext(stack_path)[1]
	if ext == ".hdf":
		splitter = ":"
	elif ext == ".h5":
		splitter = "/"
	else:
		raise octvi.exceptions.FileTypeError("File must be of format .hdf or .h5")

	## loop over all subdatasets
	outSds = []
	ds = gdal.Open(stack_path,0) # open stack as gdal dataset
	for sd in ds.GetSubDatasets():
		sdName = sd[0].split(splitter)[-1] # split name out of path
		outSds.append(sdName.strip("\"")) # strip away quotes

	return outSds

def datasetToPath(stack_path,dataset_name) -> str:
	## parsing arguments
	ext = os.path.splitext(stack_path)[1]
	if ext == ".hdf":
		splitter = ":"
	elif ext == ".h5":
		splitter = "/"
	else:
		raise octvi.exceptions.FileTypeError("File must be of format .hdf or .h5")

	## searching heirarchy for matching subdataset
	outSd = None
	ds = gdal.Open(stack_path,0) # open stack as gdal dataset
	for sd in ds.GetSubDatasets():
		sdName = sd[0].split(splitter)[-1]
		if sdName.strip("\"") == dataset_name:
			outSd = sd[0]

	if outSd is None:
		raise octvi.exceptions.DatasetNotFoundError(f"Dataset '{dataset_name}' not found in '{os.path.basename(stack_path)}'")

	return outSd

def datasetToArray(stack_path,dataset_name) -> "numpy array":
	"""
	This function copies a specified subdataset from a heirarchical format
	(such as HDF or NetCDF) to a single file such as a Tiff.

	...

	Parameters
	----------

	stack_path: str
		Full path to heirarchical file containing the desired subdataset
	dataset_name: str
		Name of desired subdataset, as it appears in the heirarchical file
	"""

	sd = datasetToPath(stack_path, dataset_name)

	## return subdataset as numpy array
	subDs = gdal.Open(sd, 0)
	subDs_band = subDs.GetRasterBand(1)
	return BandReadAsArray(subDs_band)

def datasetToRaster(stack_path,dataset_name, out_path,dtype = None) -> None:
	"""
	Wrapper for extractAsArray and arrayToRaster which pulls
	subdataset from hdf or h5 file and saves to new location.

	...

	Arguments
	---------

	stack_path: str
	dataset_name: str
	out_path: str

	"""

	sd_array = datasetToArray(stack_path, dataset_name)
	return octvi.array.toRaster(sd_array, out_path, model_file = datasetToPath(stack_path, dataset_name),dtype=dtype)

def gcviToArray(in_stack) -> "numpy array":
	"""
	This function finds the correct Green and NIR bands
	from a hierarchical file, calculates an GCVI array,
	and returns the outpus in numpy array format.

	Valid input formats are MODIS HDF or VIIRS HDF5 (h5).

	...

	Parameters
	----------

	in_stack: str
		Full path to input hierarchical file

	"""

	suffix = os.path.basename(in_stack).split(".")[0][3:7]

	# check whether it's an ndvi product
	if suffix == "09Q4" or suffix == "13Q4":
		arr_ndvi = datasetToArray(in_stack, "250m 8 days NDVI")

	elif suffix == "13Q1":
		arr_ndvi = datasetToArray(in_stack, "250m 16 days NDVI")

	elif suffix == "09CM":
		sdName_grn = "Coarse Resolution Surface Reflectance Band 4"
		sdName_nir = "Coarse Resolution Surface Reflectance Band 2"

		## extract red and nir bands from stack
		arr_grn = datasetToArray(in_stack,sdName_grn)
		arr_nir = datasetToArray(in_stack,sdName_nir)

		## perform calculation
		arr_gcvi = octvi.array.calcGcvi(arr_grn,arr_nir)

	else:
		## determine correct band subdataset names
		ext = os.path.splitext(in_stack)[1]
		if ext == ".hdf":
			sdName_grn = "sur_refl_b04"
			sdName_nir = "sur_refl_b02"
		elif ext == ".h5":
			sdName_grn = "SurfReflect_I4"
			sdName_nir = "SurfReflect_I2"
		else:
			raise octvi.exceptions.FileTypeError("File must be of type .hdf or .h5")

		## extract red and nir bands from stack
		arr_grn = datasetToArray(in_stack,sdName_grn)
		arr_nir = datasetToArray(in_stack,sdName_nir)

		## perform calculation
		arr_gcvi = octvi.array.calcGcvi(arr_grn,arr_nir)

	return arr_gcvi

def ndviToArray(in_stack) -> "numpy array":
	"""
	This function finds the correct Red and NIR bands
	from a hierarchical file, calculates an NDVI array,
	and returns the outpus in numpy array format.

	Valid input formats are MODIS HDF or VIIRS HDF5 (h5).

	...

	Parameters
	----------

	in_stack: str
		Full path to input hierarchical file

	"""

	suffix = os.path.basename(in_stack).split(".")[0][3:7]

	# check whether it's an ndvi product
	if suffix == "09Q4" or suffix == "13Q4":
		arr_ndvi = datasetToArray(in_stack, "250m 8 days NDVI")

	elif suffix == "13Q1":
		arr_ndvi = datasetToArray(in_stack, "250m 16 days NDVI")

	elif suffix == "09CM":
		sdName_red = "Coarse Resolution Surface Reflectance Band 1"
		sdName_nir = "Coarse Resolution Surface Reflectance Band 2"

		## extract red and nir bands from stack
		arr_red = datasetToArray(in_stack,sdName_red)
		arr_nir = datasetToArray(in_stack,sdName_nir)

		## perform calculation
		arr_ndvi = octvi.array.calcNdvi(arr_red,arr_nir)

	else:
		## determine correct band subdataset names
		ext = os.path.splitext(in_stack)[1]
		if ext == ".hdf":
			sdName_red = "sur_refl_b01"
			sdName_nir = "sur_refl_b02"
		elif ext == ".h5":
			sdName_red = "SurfReflect_I1"
			sdName_nir = "SurfReflect_I2"
		else:
			raise octvi.exceptions.FileTypeError("File must be of type .hdf or .h5")

		## extract red and nir bands from stack
		arr_red = datasetToArray(in_stack,sdName_red)
		arr_nir = datasetToArray(in_stack,sdName_nir)

		## perform calculation
		arr_ndvi = octvi.array.calcNdvi(arr_red,arr_nir)

	return arr_ndvi

def gcviToRaster(in_stack,out_path) -> str:
	"""
	This function directly converts a hierarchical data
	file into an GCVI raster.

	Returns the string path to the output file
	"""

	# create gcvi array
	gcviArray = gcviToArray(in_stack)

	# apply cloud, shadow, and water masks
	gcviArray = octvi.array.mask(gcviArray, in_stack)

	sample_sd = getDatasetNames(in_stack)[0]

	#ext = os.path.splitext(in_stack)[1]
	#if ext == ".hdf":
		#sample_sd = "sur_refl_b01"
	#elif ext == ".h5":
		#sample_sd = "SurfReflect_I1"
	#else:
		#raise octvi.exceptions.FileTypeError("File must be of format .hdf or .h5")

	octvi.array.toRaster(ndviArray,out_path,datasetToPath(in_stack,sample_sd))

	return out_path

def ndviToRaster(in_stack,out_path) -> str:
	"""
	This function directly converts a hierarchical data
	file into an NDVI raster.

	Returns the string path to the output file
	"""

	# create ndvi array
	ndviArray = ndviToArray(in_stack)

	# apply cloud, shadow, and water masks
	ndviArray = octvi.array.mask(ndviArray, in_stack)

	sample_sd = getDatasetNames(in_stack)[0]

	#ext = os.path.splitext(in_stack)[1]
	#if ext == ".hdf":
		#sample_sd = "sur_refl_b01"
	#elif ext == ".h5":
		#sample_sd = "SurfReflect_I1"
	#else:
		#raise octvi.exceptions.FileTypeError("File must be of format .hdf or .h5")

	octvi.array.toRaster(ndviArray,out_path,datasetToPath(in_stack,sample_sd))

	return out_path

def cmgToViewAngArray(source_stack) -> "numpy array":
	"""
	This function takes the path to a M*D CMG file, and returns
	the view angle of each pixel. Ephemeral water pixels are 
	set to 999, to be used as a last resort in compositing.

	Returns a numpy array of the same dimensions as the input raster.

	***

	Parameters
	----------
	source_stack:str
		Path to the M*D CMG .hdf file on disk
	"""
	vang_arr = datasetToArray(source_stack,"Coarse Resolution View Zenith Angle")
	state_arr = datasetToArray(source_stack,"Coarse Resolution State QA")
	water = ((state_arr & 0b111000)) # check bits
	vang_arr[water==32]=9999 # ephemeral water???
	return vang_arr

def cmgListToWaterArray(stacks:list) -> "numpy array":
	"""
	This function takes a list of CMG .hdf files, and returns
	a binary array, with "0" for non-water pixels and "1" for
	water pixels. If any file flags water in a pixel, its value
	is stored as "1"

	***

	Parameters
	----------
	stacks:list
		List of hdf filepaths (M*D**CMG) 
	"""
	water_list = []
	for source_stack in stacks:
		state_arr = datasetToArray(source_stack,"Coarse Resolution State QA")
		water = ((state_arr & 0b111000)) # check bits
		water[water==56]=1 # deep ocean
		water[water==48]=1 # continental/moderate ocean
		water[water==24]=1 # shallow inland water
		water[water==40]=1 # deep inland water
		water[water==0]=1 # shallow ocean
		water[state_arr==0]=0
		water[water!=1]=0 # set non-water to zero
		water_list.append(water)
	water_final = np.maximum.reduce(water_list)
	return water_final

def cmgToRankArray(source_stack) -> "numpy array":
	"""
	This function takes the path to a MOD**CMG file, and returns 
	the rank of each pixel, as defined on page 7 of the MOD09 user
	guide (http://modis-sr.ltdri.org/guide/MOD09_UserGuide_v1.4.pdf)

	Returns a numpy array of the same dimensions as the input raster

	***

	Parameters
	----------
	source_stack:str
		Path to the MOD**CMG .hdf file on disk
	"""
	qa_arr = datasetToArray(source_stack,"Coarse Resolution QA")
	state_arr = datasetToArray(source_stack,"Coarse Resolution State QA")
	vang_arr = datasetToArray(source_stack,"Coarse Resolution View Zenith Angle")
	vang_arr[vang_arr<=0]=9999
	sang_arr = datasetToArray(source_stack,"Coarse Resolution Solar Zenith Angle")
	rank_arr = np.full(qa_arr.shape,10) # empty rank array

	## perform the ranking!
	logging.debug("--rank 9: SNOW")
	SNOW = ((state_arr & 0b1000000000000) | (state_arr & 0b1000000000000000)) # state bit 12 OR 15
	rank_arr[SNOW>0]=9 # snow
	del SNOW
	logging.debug("--rank 8: HIGHAEROSOL")
	HIGHAEROSOL=(state_arr & 0b11000000) # state bits 6 AND 7
	rank_arr[HIGHAEROSOL==192]=8
	del HIGHAEROSOL
	logging.debug("--rank 7: CLIMAEROSOL")
	CLIMAEROSOL=(state_arr & 0b11000000) # state bits 6 & 7
	#CLIMAEROSOL=(cloudMask & 0b100000000000000) # cloudMask bit 14
	rank_arr[CLIMAEROSOL==0]=7 # default aerosol level
	del CLIMAEROSOL
	logging.debug("--rank 6: UNCORRECTED")
	UNCORRECTED = (qa_arr & 0b11) # qa bits 0 AND 1
	rank_arr[UNCORRECTED==3]=6 # flagged uncorrected
	del UNCORRECTED
	logging.debug("--rank 5: SHADOW")
	SHADOW = (state_arr & 0b100) # state bit 2
	rank_arr[SHADOW==4]=5 # cloud shadow
	del SHADOW
	logging.debug("--rank 4: CLOUDY")
	# set adj to 11 and internal to 12 to verify in qa output
	CLOUDY = ((state_arr & 0b11)) # state bit 0 OR bit 1 OR bit 10 OR bit 13
	#rank_arr[CLOUDY!=0]=4 # cloud pixel
	del CLOUDY
	CLOUDADJ = (state_arr & 0b10000000000000)
	#rank_arr[CLOUDADJ>0]=4 # adjacent to cloud
	del CLOUDADJ
	CLOUDINT = (state_arr & 0b10000000000)
	rank_arr[CLOUDINT>0]=4
	del CLOUDINT
	logging.debug("--rank 3: HIGHVIEW")
	rank_arr[sang_arr>(85/0.01)]=3 # HIGHVIEW
	logging.debug("--rank 2: LOWSUN")
	rank_arr[vang_arr>(60/0.01)]=2 # LOWSUN
	# BAD pixels
	logging.debug("--rank 1: BAD pixels") # qa bits (2-5 OR 6-9 == 1110)
	BAD = ((qa_arr & 0b111100) | (qa_arr & 0b1110000000))
	rank_arr[BAD==112]=1
	rank_arr[BAD==896]=1
	rank_arr[BAD==952]=1
	del BAD

	logging.debug("-building water mask")
	water = ((state_arr & 0b111000)) # check bits
	water[water==56]=1 # deep ocean
	water[water==48]=1 # continental/moderate ocean
	water[water==24]=1 # shallow inland water
	water[water==40]=1 # deep inland water
	water[water==0]=1 # shallow ocean
	rank_arr[water==1]=0
	vang_arr[water==32]=9999 # ephemeral water???
	water[state_arr==0]=0
	water[water!=1]=0 # set non-water to zero

	# return the results
	return rank_arr

def cmgBestNdviPixels(input_stacks:list) -> "numpy array":
	"""
	This function takes a list of hdf stack paths, and
	returns the 'best' NDVI value for each pixel location,
	determined through the ranking method (see
	cmgToRankArray() for details). 

	***

	Parameters
	----------
	input_stacks:list
		A list of strings, each pointing to a MOD**CMG hdf file
		on disk
	"""

	rankArrays = [cmgToRankArray(hdf) for hdf in input_stacks]
	vangArrays = [cmgToViewAngArray(hdf) for hdf in input_stacks]
	ndviArrays = [ndviToArray(hdf) for hdf in input_stacks]
	#ndviArrays = [octvi.array.mask(ndviToArray(hdf),hdf) for hdf in input_stacks]

	# no nodata wanted
	for i in range(len(rankArrays)):
		rankArrays[i][ndviArrays[i] == -3000] = 0

	idealRank = np.maximum.reduce(rankArrays)

	# mask non-ideal view angles
	for i in range(len(vangArrays)):
		vangArrays[i][rankArrays[i] != idealRank] = 9998
		vangArrays[i][vangArrays[i] == 0] = 9997

	idealVang = np.minimum.reduce(vangArrays)
	#print("Max vang:")
	#print(np.amax(idealVang))
	#octvi.array.toRaster(idealVang,"C:/temp/MOD09CMG.VANG.tif",input_stacks[0])
	#octvi.array.toRaster(idealRank,"C:/temp/MOD09CMG.RANK.tif",input_stacks[0])

	finalNdvi = np.full(ndviArrays[0].shape,-3000)

	# mask each ndviArray to only where it matches ideal rank
	for i in range(len(ndviArrays)):
		finalNdvi[vangArrays[i] == idealVang] = ndviArrays[i][vangArrays[i] == idealVang]

	# mask out ranks that are too low
	finalNdvi[idealRank <=7] = -3000

	# mask water
	water = cmgListToWaterArray(input_stacks)
	finalNdvi[water==1] = -3000

	# return result
	return finalNdvi

def cmgBestGcviPixels(input_stacks:list) -> "numpy array":
	"""
	This function takes a list of hdf stack paths, and
	returns the 'best' GCVI value for each pixel location,
	determined through the ranking method (see
	cmgToRankArray() for details).

	***

	Parameters
	----------
	input_stacks:list
		A list of strings, each pointing to a MOD**CMG hdf file
		on disk
	"""

	rankArrays = [cmgToRankArray(hdf) for hdf in input_stacks]
	vangArrays = [cmgToViewAngArray(hdf) for hdf in input_stacks]
	gcviArrays = [gcviToArray(hdf) for hdf in input_stacks]
	#ndviArrays = [octvi.array.mask(ndviToArray(hdf),hdf) for hdf in input_stacks]

	# no nodata wanted
	for i in range(len(rankArrays)):
		rankArrays[i][gcviArrays[i] == -3000] = 0

	idealRank = np.maximum.reduce(rankArrays)

	# mask non-ideal view angles
	for i in range(len(vangArrays)):
		vangArrays[i][rankArrays[i] != idealRank] = 9998
		vangArrays[i][vangArrays[i] == 0] = 9997

	idealVang = np.minimum.reduce(vangArrays)
	#print("Max vang:")
	#print(np.amax(idealVang))
	#octvi.array.toRaster(idealVang,"C:/temp/MOD09CMG.VANG.tif",input_stacks[0])
	#octvi.array.toRaster(idealRank,"C:/temp/MOD09CMG.RANK.tif",input_stacks[0])

	finalGcvi = np.full(gcviArrays[0].shape,-3000)

	# mask each gcviArray to only where it matches ideal rank
	for i in range(len(gcviArrays)):
		finalGcvi[vangArrays[i] == idealVang] = gcviArrays[i][vangArrays[i] == idealVang]

	# mask out ranks that are too low
	finalGcvi[idealRank <=7] = -3000

	# mask water
	water = cmgListToWaterArray(input_stacks)
	finalGcvi[water==1] = -3000

	# return result
	return finalGcvi