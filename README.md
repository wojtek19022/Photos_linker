# Photos_linker
That is a tool for creating points from locations where picture was taken and make user avaliable to click on this picture.

Plugin workflow:
- user inputs folder to use pictures which have location,
- from selected pictures, plugin exports location and creates points that have directory of a taken picture in same location,
- if photo doesn't have metadata, user will be notified about it,
- user can select whether want to create an Shapefile or Geopackage in selected location or add it to a project layers in memory.

Output data is projected in polish geographic coordinate system - PL-1992.
