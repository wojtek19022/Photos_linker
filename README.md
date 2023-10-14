# Photo linker
That is a tool for creating points from locations where picture was taken and make user avaliable to click on this picture.

Plugin workflow:
- user inputs folder to use pictures which have location,
- from selected pictures, plugin exports location and creates points that have directory of a taken picture in same location,
- if photo doesn't have metadata, user will be notified about it,
- user can select whether want to create an Shapefile or Geopackage in selected location or add it to a project layers in memory.

Output data is projected in world geographic coordinate system - WGS-84. If in picture is saved and information about picture direction, it will be shown by arrow. If not, in the picture location will be a point.

Also in the pictures localizations, every signle picture that has metadata, is assigned its' time when the picture had been captured.

<p align = "center">Created by <strong>Wojciech Sołyga</strong> in Python.</p><br>
<p align = "center">Last updated: <strong>14.10.2023 r.</strong></p>
