# Python sripts to enhance Therion Shapefile outputs

Set of Python scripts to enhance Therion Shapefile outputs to be used more easylly through QGIS and Merging Maps apps.

## Usage

### Add altitude and easting/northing values in the attribrut tables

```
usage: >>> AddAltPoint(pathshp = "path_to_the_shp_folder", outputspath = "path_where_to_write_output_files")
```

Create a new shapefile with all the stations 3D, with their geometry as attribut table. It uses the stations3d.shp and points2d.shp built by Therion.

Before to run this script, you must build the stations3d.shp and points2d.shp with Therion.

### Clean the lines and areas shapefiles

```
usage: >>> ThCutAreas(pathshp = "path_to_the_shp_folder", outputspath = "path_where_to_write_output_files")
```

Create new shapefiles of lines and areas, but with only the info inside the cave outline if the option -clip is set to on or null, except for centerlines and label lines. It uses the files outline2d.shp, lines2d.shp and areas2d.shp built by Therion.

Before to run this script, you must build the files outline2d.shp, lines2d.shp and areas2d.shp with Therion and verify the validity of their geometry.

### Convert all the necessary Therion shapefile into gpkg format

```
usage: >>> shp2gpkg(pathshp = "path_to_the_shp_folder", outputspath = "path_where_to_write_output_files")
```
Convert the shapefiles outline2d.shp, shots3d.shp, and walls3d.shp into the gpkg format.

### Perform all enhancing in once

```
usage: >>> runThGIS(pathshp = "path_to_the_shp_folder", outputspath = "path_where_to_write_output_files")
```

Run the three scripts in once.

## Licence

This script is under the GNU GPL-3.0-or-later licence.

## Author

Xavier Robert (xavier.robert@ird.fr)

## Citation

If used, please cite :

Robert X. (2025), pyThGIS, a Python code to clean the shp Therion output. DOI:10.5281/zenodo.15078040

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15078040.svg)](https://doi.org/10.5281/zenodo.15078040)

