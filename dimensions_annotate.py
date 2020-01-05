# -*- coding: utf-8 -*-
# !/usr/bin/python

import math

import inkscapeMadeEasy_Base as inkBase
import inkscapeMadeEasy_Draw as inkDraw
import numpy as np

import inkex
import simpletransform, simplestyle

class DimensionsAnnotate(inkBase.inkscapeMadeEasy):
    def __init__(self):
        inkBase.inkscapeMadeEasy.__init__(self)

        self.OptionParser.add_option(
            "--customContent", action="store", type="string",
            dest="customContent", default='')

        
        ########################################
        # General Options 
        ########################################
        self.OptionParser.add_option(
            "--fontSize", action="store", type="float", 
            dest="fontSize", default=1.0)
        self.OptionParser.add_option(
            "--lineWidthProp", action="store", type="float", 
            dest="lineWidthProp", default=1.0)
        self.OptionParser.add_option(
            "--arrowSizeProp", action="store", type="float", 
            dest="arrowSizeProp", default=1.0)
        
        ########################################
        # Colors 
        ########################################
        self.OptionParser.add_option(
            "--textColor", action="store", type="string", 
            dest="textColorOption", default='black')
        self.OptionParser.add_option(
            "--lineColor", action="store", type="string", 
            dest="lineColorOption", default='black')

        

    def effect(self):
        so = self.options

        self.documentUnit = self.getDocumentUnit()

        # Get the document scale
        try:
            elem = self.getElemFromXpath('/svg:svg')
            width = self.getElemAtrib(elem, 'width')
            width = width.replace(self.documentUnit, '')
            width = float(width)
            elem = self.getElemFromXpath('/svg:svg')
            view_width = self.getElemAtrib(elem, 'viewBox')
            view_width = str.split(view_width, ' ')[2]
            view_width = float(view_width)
            self.documentScale = view_width / width
        except:
            self.documentScale = 1
        
        root_layer = self.getcurrentLayer()

        # Colors
        self.textColor = inkDraw.color.parseColorPicker(
            so.textColorOption, '0')[0]
        self.lineColor = inkDraw.color.parseColorPicker(
            so.lineColorOption, '0')[0]

        # Text Size and Font Style
        inkDraw.useLatex = False
        self.fontSize = so.fontSize * self.documentScale

        self.textStyle = inkDraw.textStyle.setSimpleColor(
            self.fontSize / 0.75, justification = 'center',
            textColor = self.textColor)

        self.lineWidth = (self.fontSize / 10.0) * so.lineWidthProp
        self.arrowSize = (self.fontSize) * so.arrowSizeProp
        

        # Linestyles
        renameMode = 2  # 0: do not create, , 1: overwrite  2: new name
        # I have to scale it with respect to the lineWidth since marker's size
        # is associated to width=1.0 
        scaleMarker = 'scale (' + str(1.0 / self.lineWidth) + ')'
        translateMarker = 'translate (%s,0)' % self.arrowSize
        markerPath = 'M 0.0,0.0 L %f,%f L %f,%f L 0.0,0.0 z ' % (
            -self.arrowSize,
            self.arrowSize * math.tan(10 * math.pi / 180.0),
            -self.arrowSize,
            -self.arrowSize * math.tan(10 * math.pi / 180.0))

        arrowStart = inkDraw.marker.createMarker(
            self, 'DimmArrow_Start', markerPath,
            renameMode, strokeColor=None,
            fillColor = self.lineColor,
            markerTransform = scaleMarker + 'rotate(180)' + translateMarker)

        self.annotationLineStyle = inkDraw.lineStyle.set(
            lineWidth = self.lineWidth,
            lineColor = self.lineColor,
            markerStart = arrowStart,
            lineJoin = 'miter', lineCap = 'square')

        for id, element in self.selected.iteritems():
            if (element.tag == inkex.addNS('path', 'svg') or
                element.tag == 'path'):
                self.drawAnnotationArrow(
                    root_layer, element,
                    contents = so.customContent)
                self.removeElement(element)


                
    def drawAnnotationArrow(self, parent, auxElement, label='annotation',
                            contents='textHere', nLines=1, scale=1.0):
        """ draws annotation Arrow

        parent: parent object
        auxElement: path with 3 points. the first will be the tip of the arrow,
                    the next two demarks the area of the text
        label: label of the object (it can be repeated)
        contents: contents string
        nLines: number of lines of text
        """

        group = self.createGroup(parent, label)

        points = self.getPoints(auxElement)

        if len(points) < 2:
            return None

        t_vector = np.array(points[0]) - np.array(points[1])
        angle = math.atan2(t_vector[1], t_vector[0]) * 180.0 / math.pi

        t_norm = np.linalg.norm(t_vector)
        if t_norm == 0:
            return None
        
        t_versor = t_vector / t_norm

        P1 = np.array(points[0]) - t_versor * self.arrowSize
        P1 = P1.tolist()

        P2 = points[1]

        contents = contents.replace('\\\\', '\\n')
        splitCont = contents.split('\\n')
        nLines = len(splitCont)

        xOffset = self.fontSize * 7 / 10
        justif = 'br'
        if abs(angle) - 90 >= 0:
            justif = 'bl'
            xOffset *= -1
        
        if len(points) < 3:
            P3 = [P2[0] - xOffset * (1/2 + len(splitCont[-1])),
                  P2[1]]
        else:
            P3 = points[2]

        inkDraw.line.absCoords(
            group, [P1, P2, P3],
            offset = [0, 0],
            label = 'dim',
            lineStyle = self.annotationLineStyle)

        # TODO: Offset X
        pos = [P2[0] - xOffset/2,
               P2[1] - 
               self.fontSize / 3.0 -
               (nLines - 1) * self.fontSize * 1.2]

        text = inkDraw.text.latex(
            self, group, contents, pos,
            textColor = self.textColor,
            fontSize = self.fontSize,
            refPoint = justif)

        # [Pmin, Pmax] = self.getBoundingBox(text)

        return group




if __name__ == '__main__':
    dimension = DimensionsAnnotate()
    dimension.affect()
