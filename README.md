# octvi
Python package for downloading, mosaicking, or compositing MODIS-scale NDVI imagery

# Updates

## New in Version 2.1.0

Support has been added for the product MOD09A1, along with Normalized Difference Water Index for that product.

## New in Version 2.0.4

A bug in the `octviconfig` console script has been fixed. Setting a personal NASA app key is now possible.

## New in Version 2.0.2

The default masking criteria for MxD09Q1, MxD13Q1, and MxD13Q4N imagery have been relaxed. MxD09Q1 files no longer remove "average" aerosol pixels, and pixels flagged as "cloud-adjacent", which were formerly removed, are now kept. For MxD13 imagery, masking previously relied on the simple "pixel reliability index." This method has been replaced with a more granular masking schema, closely resembling that used for MxD09 data.

## New in Version 2.0.0

Downloading from the NASA distributed archives (DAACs) requires a personal app key. This key was previously provided as part of the `octvi` distribution, but this is no longer the case as of Version 2.0.0. Instead, users must configure the module using a new console script, `octviconfig`. After installation, run `octviconfig` to prompt the input of your personal app key. Information on obtaining app keys can be found at https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/data-download-scripts/#tokens.

# Motivation
I work on development of the Global Agriculture Monitoring (GLAM) system. A core feature of the system is the ability to display large amounts of Vegetation Index (VI) imagery, pulled from sources like the MODIS and VIIRS satellite sensors. Obviously, displaying that imagery through our system requires the ability to download it from its source. This is harder than it sounds, especially when we also want to extract specific subdatasets, convert to a different file format, and mosaic dozens of individual "tiles" into a single global image.

This package started out as a local tool for that very purpose. The name "octvi" comes from the fact that, at first, I planned to restrict functionality to 8-day (oct) vegetation indices (vi). Over time, though, I realized it was fairly simple to support more imagery products, including 16-day vegetation indices and even DIY multi-day composites. When other researchers in my department started asking to use the package, I realized it needed to be more accessible.

# Features
The primary functionality of the `octvi` module is the creation of global mosaics of Normalized Difference Vegetation Index (NDVI) imagery. Supported imagery products include:

* MODIS 8-day NDVI
  * Terra (MOD09Q1)
  * Aqua (MYD09Q1)
* MODIS 16-day NDVI
  * Terra (MOD13Q1)
  * Aqua (MYD13Q1)
* VIIRS 8-day NDVI (VNP09H1)
* LANCE Near Real-Time
  * MODIS 8-day Terra (MOD09Q1N)
  * MODIS 16-day Terra (MOD13Q4N)
* MODIS 8-day Climate Modeling Grid (CMG)-scale NDVI/GCVI (MOD09CMG; custom compositing)
  * Note that MOD09CMG supports Green Chlorophyll Vegetation Index (GCVI) as well as NDVI

# Code Example

```python
import octvi # import module

# create a list of all days in January 2019 for which there exists valid VNP09H1 imagery
viirsJanuaryDates = octvi.url.getDates("VNP09H1","2019-01")

# generate global NDVI mosaic of MOD09Q1 data for an 8-day period starting on January 1st, 2019
octvi.globalVi("MOD09Q1","2019-01-01","C:/temp/example_standard.tif")

# generate custome composite of CMG-scale GCVI for an 8-day period starting on January 1st, 2019
octvi.globalVi("MOD09CMG","2019-01-01","C:/temp/example_cmg.tif",vi="GCVI")
```

# How to Use

## In Python

The `octvi` package contains four submodules: `url`, `extract`, `array`, and `exceptions`. Most of the features you will want, though, are in the top-level module.

The core functionality is shown in the code example above. Once the package is installed, you can import it in a script or REPL, and then use all the submodules freely. When `octvi` is imported, all submodules are also automatically imported and their namespaces can be accessed as shown with `octvi.url.getDates()` above.

## On the Command Line

The package comes with one console script entry point: `octvidownload`. This script takes three arguments: product name (e.g. 'MOD09Q1'), date in %Y-%m-%d format (e.g. '2019-01-01') and output directory. Calling the script creates a global NDVI mosaic of the requested product on the requested day. If the product is daily Climate Modeling Grid-scale imagery (e.g. MOD09CMG), the script instead produces its own 8-day composite, with the 'date' argument being the first day of the compositing period.

# License
MIT License

Copyright (c) 2020 F. Dan O'Neill

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
