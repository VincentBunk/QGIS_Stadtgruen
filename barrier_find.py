# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import (
    QgsProcessing,
    QgsFeatureSink,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsMessageLog,
    QgsGeometry,
)

from qgis.gui import (
    QgsMessageBar,
)


from qgis.PyQt.QtWidgets import (
    QSizePolicy,
    QPushButton,
    QDialog,
    QGridLayout,
    QDialogButtonBox,
)

from qgis import processing


class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    INPUT_RADIUS = 'INPUT_RADIUS'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'myscript'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('My Script')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Example scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'examplescripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Example algorithm short description")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.INPUT_RADIUS,
                description=self.tr('Radius'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.3,
                optional=False,
                minValue=0,
                maxValue=100
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs()
        )

        # Send some information to the user
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        # If sink was not created, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSinkError method to return a standard
        # helper text for when a sink cannot be evaluated
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        
        #input_radius = self.parameterAsNumber(
        #    parameters,
        #    self.INPUT_RADIUS,
        #    context
        #)
        
        radius = 0.3

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        
            # 50%
            biotopanteil_ziel = 5000000
            
            biotopanteil = feature["biotopanteil_prozent"]
            tile_id = feature["id"]
            top_coord = int(feature["top"])
            right_coord = int(feature["right"])
            bottom_coord = int(feature["bottom"])
            left_coord = int(feature["left"])
            is_green = "false"
            green_neighbour = "false"
            neighbours = [0,0,0,0,0,0]
        
            
            if biotopanteil >= biotopanteil_ziel:
                is_green = "true"
                
                # check surrounding tiles for green
                for current, inner_feature in enumerate(features):
                    # item is not current item
                    if inner_feature["id"] != tile_id:
                        if inner_feature["biotopanteil_prozent"] >= biotopanteil_ziel:
                            green_neighbour = "true"
                            
                            # ToDo: Bundle into function
                            # check top neighbour
                            if top_coord - radius <= int(inner_feature["bottom"]) <= top_coord + radius:
                                # Problem here!
                                if right_coord - radius <= int(inner_feature["right"]) <= right_coord + radius:
                                    feedback.pushInfo("oben")
                                    neighbours[0] = inner_feature["id"]
                            
                            # check top right neighbour
                            elif top_coord - radius <= int(inner_feature["left"]) <= top_coord + radius:
                                if right_coord - radius <= inner_feature["bottom"] <= right_coord + radius:
                                    feedback.pushInfo("rechts oben")
                                    neighbours[1] = inner_feature["id"]
                                    
                            # check bottom right neighbour
                            elif bottom_coord - radius <= int(inner_feature["left"]) <= bottom_coord + radius:
                                if right_coord - radius <= inner_feature["top"] <= right_coord + radius:
                                    feedback.pushInfo("rechts unten")
                                    neighbours[2] = inner_feature["id"]
                                    
                            # check bottom neighbour
                            elif bottom_coord - radius <= int(inner_feature["top"]) <= bottom_coord + radius:
                                if right_coord - radius <= inner_feature["right"] <= right_coord + radius:
                                    feedback.pushInfo("unten")
                                    neighbours[3] = inner_feature["id"]
                                    
                            # check bottom left neighbour
                            elif bottom_coord - radius <= int(inner_feature["right"]) <= bottom_coord + radius:
                                if left_coord - radius <= inner_feature["top"] <= left_coord + radius:
                                    feedback.pushInfo("links unten")
                                    neighbours[4] = inner_feature["id"]
                            
                            # check top left neighbour
                            elif top_coord - radius <= int(inner_feature["right"]) <= top_coord + radius:
                                if left_coord - radius <= inner_feature["bottom"] <= left_coord + radius:
                                    feedback.pushInfo("links oben")
                                    neighbours[5] = inner_feature["id"]
                
            feedback.pushInfo("Item ID: "+str(tile_id)+", Biotopanteil: "+str(biotopanteil)+", Grün: "+is_green+", Hat grüne Nachbarn: "+green_neighbour)
            
            # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

            # Add a feature in the sink
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        # To run another Processing algorithm as part of this algorithm, you can use
        # processing.run(...). Make sure you pass the current context and feedback
        # to processing.run to ensure that all temporary layer outputs are available
        # to the executed algorithm, and that the executed algorithm can send feedback
        # reports to the user (and correctly handle cancellation and progress reports!)
        if False:
            buffered_layer = processing.run("native:buffer", {
                'INPUT': dest_id,
                'DISTANCE': 1.5,
                'SEGMENTS': 5,
                'END_CAP_STYLE': 0,
                'JOIN_STYLE': 0,
                'MITER_LIMIT': 2,
                'DISSOLVE': False,
                'OUTPUT': 'memory:'
            }, context=context, feedback=feedback)['OUTPUT']

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: dest_id}
