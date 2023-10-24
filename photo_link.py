# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Photo_Link
                                 A QGIS plugin
 That is a plugin to link photos with points in shapefiles
                              -------------------
        begin                : 2023-05-13
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Wojciech Sołyga
        email                : wojciech.solyga2@gmail.com

***************************************************************************/"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication ,QVariant
from qgis.PyQt.QtGui import QIcon, QColor, QBrush
from qgis.PyQt.QtWidgets import QAction, QPushButton, QMessageBox, QLineEdit
from qgis.core import (QgsVectorLayer, QgsProject, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorFileWriter, QgsRasterLayer,
                       QgsCoordinateReferenceSystem, QgsAction)


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .photo_link_dialog import Photo_LinkDialog
import os.path
import os
import subprocess
import sys
import processing
import pip


class Photo_Link:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Photo_Link_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Photo linker')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        self.project = QgsProject.instance()
        self.canvas = self.iface.mapCanvas()

        # check if exif is installed on computer

        libraries = os.path.dirname(sys.executable).replace(os.path.dirname(sys.executable).split("\\")[-1],
                                                            "\\apps\\Python39\\Lib\\site-packages")
        print(libraries)
        if 'exif' not in [file for file in os.listdir(libraries)]:
            subprocess.check_call(['python', '-m', 'pip', 'install', 'exif'])

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Photo_Link', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/photo_link/icon.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Photos_linker/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Generate Images locations'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True
        self.dlg = Photo_LinkDialog()



    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Photo linker'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""
        from exif import Image
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = Photo_LinkDialog()

            self.dlg.OK.clicked.connect(self.linker)
            self.dlg.fileName.fileChanged.connect(self.folder_input)
            self.dlg.fileName_2.fileChanged.connect(self.folder_output)

        # show the dialog
        self.dlg.show()

        self.dlg.closeEvent = self.close
        # Run the dialog event loop
        # result = self.dlg.exec_()

    def folder_input(self):
        self.input = self.dlg.fileName.filePath()

    def folder_output(self):
        self.output = self.dlg.fileName_2.filePath()

    def linker(self):
        from exif import Image
        lista = []
        coordinates_X = []
        coordinates_Y = []
        has_GPS = []
        X_pop = []
        Y_pop = []
        sciezka = []
        azimuths = []
        dates = []
        liczba = []


        if self.dlg.fileName.filePath() == "":
            QMessageBox(QMessageBox.Warning, "Ostrzeżenie:","Nie wybrano żadnego folderu ze zdjęciami. Przed kontunuacją wybierz folder ze zdjęciami.").exec_()

        elif not os.path.isdir(self.dlg.fileName.filePath()):
            QMessageBox(QMessageBox.Warning, "Ostrzeżenie:",
                        "Ścieżka niepoprawna. Sprawdź, czy ścieżka istnieje.").exec_()
        else:
            try:
                w = os.listdir(self.input)

                for i in w:
                    if i.split(".")[-1].lower() in ["jpg","png","jpeg"]:
                        print(i)#.split(".")[-1].lower())
                        lista.append((self.input + '\\' + i))
                    else:
                        QMessageBox(QMessageBox.Warning, "Ostrzeżenie:",
                                    f"Zdjęcie {i} nie zostało dodane z powodu nieprawidłowego formatu.").exec_()

                for i in lista:
                    with open(i, 'rb') as src:
                        img = Image(src)
                        print(len([x for x in w]))
                        try:
                            if img.gps_longitude or img.gps_latitude:
                                liczba.append(i)
                                print(len(liczba))
                                has_GPS.append(i)
                                if img.gps_longitude_ref=="W":
                                    X = img.gps_longitude*(-1)
                                else:
                                    X = img.gps_longitude
                                coordinates_X.append(X)

                                if img.gps_latitude_ref == "S":
                                    Y = img.gps_latitude*(-1)
                                else:
                                    Y = img.gps_latitude
                                coordinates_Y.append(Y)

                                dates.append(img.datetime)
                                # print(i)#, X, Y)
                                try:
                                    if img.gps_img_direction:
                                        azimuth = float(img.gps_img_direction)
                                        azimuths.append(azimuth)
                                        # print("Azymut: ",float(img.gps_img_direction))

                                except:
                                    azimuths.append(-999)
                                    pass
                            elif not img.gps_longitude:
                                # lista.remove(i)
                                pass
                        except:
                            # lista.remove(i)
                            QMessageBox(QMessageBox.Warning, "Ostrzeżenie:",
                                        f"Zdjęcie {i} nie posiada zapisanej lokalizacji, sprawdź, czy przed zrobieniem zdjęcia była włączona lokalizacja.").exec_()
                            pass

                if len(coordinates_X) != 0:
                    for x, y in zip(coordinates_X, coordinates_Y):
                        X_pop.append(x[0] + x[1] / 60 + x[2] / 3600)
                        Y_pop.append(y[0] + y[1] / 60 + y[2] / 3600)

                    layers = self.project.mapLayers()

                    OSM = 'type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0'
                    OSM_layer = QgsRasterLayer(OSM, 'OpenStreetMap', 'wms')
                    root = self.project.layerTreeRoot()

                    lista_obiektow = [layer for layer in layers]

                    if not 'OpenStreetMap' in [i.name() for i in layers.values()]:
                        self.project.addMapLayer(OSM_layer,False)
                        root.insertLayer(int(len(lista_obiektow) + 1), OSM_layer)
                    else:
                        pass

                    uri = "Point?crs=EPSG:4326&field=lat:double&field=lon:double&index=yes"
                    self.project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
                    layer = QgsVectorLayer(uri, "Zdjęcia", "Memory")
                    self.project.addMapLayer(layer)
                    pr = layer.dataProvider()  # need to create a data provider
                    pr.addAttributes([QgsField("path", QVariant.String)])
                    pr.addAttributes([QgsField("azimuth", QVariant.Double)])
                    pr.addAttributes([QgsField("lenght", QVariant.Double)])
                    pr.addAttributes([QgsField("datetime", QVariant.String, len=30)])
                    layer.updateFields()

                    # Edycja symboliki warstwy

                    single_symbol_renderer = layer.renderer()
                    symbol = single_symbol_renderer.symbol()

                    styl = os.path.join(self.plugin_dir,"Styl/Styl_punkty.qml")
                    layer.loadNamedStyle(styl)

                    for r in zip(has_GPS, X_pop, Y_pop,azimuths,dates):
                        print(r)
                        sciezka.append(r[0])
                        f = QgsFeature(layer.fields())

                        f["lon"] = float(r[1])
                        f["lat"] = float(r[2])
                        f["path"] = str(r[0])
                        f["azimuth"] = float(r[3])
                        f["lenght"] = float(3)
                        f["datetime"] = str(r[4])

                        geom = QgsGeometry.fromPointXY(QgsPointXY(r[1], r[2]))
                        f.setGeometry(geom)
                        layer.dataProvider().addFeatures([f])
                        layer.updateFields()

                    # Function zooms to extent of a layer
                    print(layer.extent())
                    self.canvas.setExtent(layer.extent())
                    self.canvas.refresh()

                    # add action to open linked document
                    action = QgsAction(QgsAction.OpenUrl, 'Open file', '[% "Path" %]')
                    my_scopes = {'Layer', 'Canvas', 'Field', 'Feature'}
                    action.setActionScopes(my_scopes)

                    actionManager = layer.actions()
                    actionManager.addAction(action)

                    # The only line added from your answer
                    actionManager.setDefaultAction('Canvas', action.id())
                    action.trigger()

                    # Nadanie nowego układu współrzędnych tak, aby były dane lepiej widoczne
                    self.project.setCrs(QgsCoordinateReferenceSystem("EPSG:3857"))
                    # Zapisywanie warstwy do ścieżki lokalnej
                    if self.dlg.fileName_2.filePath() == "":
                        self.iface.messageBar().pushSuccess("Sukces","Warstwa z sukcesem została utworzona w pamięci")

                    elif not self.output.split(".")[-1] in ["shp","gpkg"]:

                        QMessageBox(QMessageBox.Warning, "Ostrzeżenie:","Ścieżka niepoprawna. Sprawdź, czy ścieżka istnieje.").exec_()

                    else:
                        transform_context = self.project.transformContext()
                        save_options = QgsVectorFileWriter.SaveVectorOptions()

                        QgsVectorFileWriter.writeAsVectorFormatV2(layer, self.output, transform_context, save_options)
                        self.iface.messageBar().pushSuccess("Sukces",
                                                            f"Obiekty z sukcesem zostały wyeksportowane do ścieżki: {self.output}")
                else:
                    pass
            except:
                lista.clear()
                coordinates_X.clear()
                coordinates_Y.clear()
                has_GPS.clear()
                X_pop.clear()
                Y_pop.clear()
                sciezka.clear()
                azimuths.clear()
                dates.clear()
                liczba.clear()



    def close(self,event):
        self.dlg.fileName.setFilePath('')
        self.dlg.fileName_2.setFilePath('')