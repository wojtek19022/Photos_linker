# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Photo_Link
                                 A QGIS plugin
 That is a plugin to link photos with points in shapefiles
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-05-13
        copyright            : (C) 2023 by Wojciech Sołyga
        email                : wojciech.solyga2@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Photo_Link class from file Photo_Link.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .photo_link import Photo_Link
    return Photo_Link(iface)
