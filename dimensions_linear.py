# -*- coding: utf-8 -*-
# !/usr/bin/python

import math

import inkscapeMadeEasy_Base as inkBase
import inkscapeMadeEasy_Draw as inkDraw
import numpy as np

import inkex
import simpletransform, simplestyle


class lineSegment(inkBase.inkscapeMadeEasy):
    def __init__(self, Pstart, Pend, normalDirection='R'):
        self.Pstart = np.array(Pstart)
        self.Pend = np.array(Pend)
        [self.length, self.theta,
         self.t_versor, self.n_versor] = self.getSegmentFromPoints(
             [Pstart, Pend],
             normalDirection)

        while self.theta < 0:
            self.theta += 2.0 * math.pi

    def getPointAtLength(self, length):
        return self.Pstart + length * self.t_versor



class DimensionsLinear(inkBase.inkscapeMadeEasy):
    def __init__(self):
        inkBase.inkscapeMadeEasy.__init__(self)

        self.OptionParser.add_option(
            "--group", action="store", type="inkbool",
            dest="group", default=False)
        self.OptionParser.add_option(
            "--direction", action="store", type="string",
            dest="direction", default='horizontal')
        self.OptionParser.add_option(
            "--side", action="store", type="string",
            dest="side", default='upperLeft')
        self.OptionParser.add_option(
            "--horizontalText", action="store", type="inkbool",
            dest="horizontalText", default=True)
        self.OptionParser.add_option(
            "--smalDimStyle", action="store", type="inkbool",
            dest="smalDimStyle", default=False)
        self.OptionParser.add_option(
            "--unit", action="store", type="string",
            dest="unit", default='doc')
        self.OptionParser.add_option(
            "--unitSymbol", action="store", type="inkbool",
            dest="unitSymbol", default=True)

        self.OptionParser.add_option(
            "--expandInches", action="store", type="inkbool",
            dest="expandInches", default=True)
        self.OptionParser.add_option(
            "--precision", action="store", type="string",
            dest="precision", default="16")
        self.OptionParser.add_option(
            "--trimzero", action="store", type="inkbool",
            dest="trimzero", default=True)

        self.OptionParser.add_option(
            "--customContent", action="store", type="string",
            dest="customContent", default='')

        
        ########################################
        # General Options 
        ########################################
        self.OptionParser.add_option(
            "--markerStyle", action="store", type="string", 
            dest="markerStyle", default='serif')

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
        self.auxLineOffset = (self.fontSize / 2.5) 
        self.auxLineExtension = (self.fontSize / 2.5)
        self.dimensionSpacing = (2.0 * self.fontSize)
        # offset between symbol and text
        self.textOffset = (self.fontSize / 2.5)  

        # Linestyles
        self.auxiliaryLineStyle = inkDraw.lineStyle.set(
            lineWidth=self.lineWidth, lineColor=self.lineColor,
            lineJoin = 'miter', lineCap = 'square')

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
            self, 'DimmArrow_Start', markerPath, renameMode, strokeColor=None,
            fillColor=self.lineColor,
            markerTransform=scaleMarker + 'rotate(180)' + translateMarker)
        arrowEnd = inkDraw.marker.createMarker(
            self, 'DimmArrow_End', markerPath, renameMode, strokeColor=None,
            fillColor=self.lineColor,
            markerTransform=scaleMarker + translateMarker)

        if so.markerStyle == 'arrow':
            self.dimensionLineStyle = inkDraw.lineStyle.set(
                lineWidth=self.lineWidth, lineColor=self.lineColor,
                markerStart=arrowStart, markerEnd=arrowEnd)

        if so.markerStyle == 'circle':
            marker = inkDraw.marker.createDotMarker(
                self, 'DimmCircle', renameMode,
                scale=0.05 / self.lineWidth * self.arrowSize, strokeColor=None,
                fillColor=self.lineColor)
            self.dimensionLineStyle = inkDraw.lineStyle.set(
                lineWidth=self.lineWidth, lineColor=self.lineColor,
                markerStart=marker, markerEnd=marker)

        if so.markerStyle == 'serif':
            markerPath = 'M -%f,%f L %f,-%f' % (
                0.5 * self.arrowSize,
                0.5 * self.arrowSize,
                0.5 * self.arrowSize,
                0.5 * self.arrowSize)
            marker = inkDraw.marker.createMarker(
                self, 'DimmSerif', markerPath, renameMode,
                strokeColor = self.lineColor,
                lineWidth = self.lineWidth * 2,
                markerTransform = scaleMarker)
            self.dimensionLineStyle = inkDraw.lineStyle.set(
                lineWidth = self.lineWidth,
                lineColor = self.lineColor,
                markerStart = marker,
                markerEnd = marker)

        self.ANGdimensionLineStyle = inkDraw.lineStyle.set(
            lineWidth = self.lineWidth, lineColor = self.lineColor,
            markerStart = arrowStart, markerEnd = arrowEnd)

        # used with small dimension
        self.ANGdimensionLineStyleSmall = inkDraw.lineStyle.set(
            lineWidth=self.lineWidth, lineColor=self.lineColor,
            markerEnd=arrowEnd,
            lineJoin = 'miter', lineCap = 'square')
        self.ANGdimensionLineStyleSmall2 = inkDraw.lineStyle.set(
            lineWidth=self.lineWidth, lineColor=self.lineColor,
            markerStart=arrowStart,
            lineJoin = 'miter', lineCap = 'square')

        ########################################
        # Begin Drawing 
        ########################################
        # Draw dimension for bounding box of whole selection
        if so.group:
            [P1, P2] = self.getPointsBB(
                self.selected.values(), so.direction, so.side)
            if P1 and P2:
                self.drawLinDim(root_layer, [P1, P2])

        # Draw dimensions for each object selected
        else:
            for id, element in self.selected.iteritems():
                if (element.tag == inkex.addNS('path', 'svg') or
                    element.tag == 'path'):
                    [P1, P2] = self.getPointsLinDim(element)
                else:
                    [P1, P2] = self.getPointsBB(
                        element, so.direction, so.side)

                if P1 and P2:
                    self.drawLinDim(root_layer, [P1, P2])


    def drawLinDim(self, parent, points):
        """ draws linear dimension

        parent: parent object
        points: list of points [P1,P2]
        """

        direction = self.options.direction
        label = 'Dim'
        customText = self.options.customContent
        unit = self.options.unit
        unitSymbol = self.options.unitSymbol
        precision = self.options.precision
        horizontalText = self.options.horizontalText
        textSide = self.options.side
        smallDimension = self.options.smalDimStyle
        trimTrailingZero = self.options.trimzero
        expandInches = self.options.expandInches
                    
        # Order the points
        P1 = np.array(points[0])
        P2 = np.array(points[1])

        if textSide == 'lowerRight':
            textSide = -1
            P1 = np.array(points[1])
            P2 = np.array(points[0])
        else:
            textSide = 1

        t_vector = P2 - P1
        angle = math.atan2(t_vector[1], t_vector[0]) * 180.0 / math.pi
        
        if angle == 0 or angle == 180:
            direction = 'horizontal'
        if abs(angle) == 90:
            direction = 'vertical'

        # Figure out the direction if AUTO         
        if direction == 'auto':
            # threshold how close to 0 or 90 degrees to be for horizontal or
            # vertical 
            parallel_threshold = 15 
            if abs(abs(angle) - 90) < parallel_threshold:
                direction = 'vertical'
            elif (abs(angle) < parallel_threshold or
                  abs(angle) > (180 - parallel_threshold)):
                direction = 'horizontal'
            else:
                direction = 'parallel'

        
        delta = [0, 0]
        
        if direction == 'parallel':
            if angle >= 45:
                P1 = np.array(points[1])
                P2 = np.array(points[0])
            if angle < 45-180:
                P1 = np.array(points[0])
                P2 = np.array(points[1])
            t_vector = P2 - P1

        if direction == 'horizontal':
            t_vector = np.array([t_vector[0], 0])
            if abs(angle) >= 90:
                textSide *= -1
            delta = [0, abs(P2[1] - P1[1])]
            
        if direction == 'vertical':
            P1 = np.array(points[0])
            P2 = np.array(points[1])
            t_vector = P2 - P1
            t_vector = np.array([0, t_vector[1]])
            delta = abs(P2[0] - P1[0])

            if abs(angle) <= 90:
                delta = [0, delta]
            else:
                delta = [delta, 0]
            textSide *= -1

        # normal vector: counter-clockwise with respect to tangent vector
        n_vector = np.array([t_vector[1], -t_vector[0]])

        # normalization
        t_norm = np.linalg.norm(t_vector)
        if t_norm == 0:
            return None
        
        t_versor = t_vector / t_norm
        n_versor = textSide * n_vector / np.linalg.norm(n_vector)

        
        # Text String
        valueStr = customText

        # If custom text is empty, calculate dimension from points
        if valueStr is None or len(valueStr.strip()) == 0:
            if unit == 'doc':
                unit = self.documentUnit
                
            value = np.linalg.norm(n_vector)                
            value = self.unit2unit(value, self.documentUnit, unit)
            value /= self.documentScale
            valueStr = value
            
            if unitSymbol and unit == 'in':
                if expandInches:
                    valueStr = self.inches2ft(valueStr)
                else:
                    valueStr = [0, valueStr]
                    
                if precision[0] == 'p':
                    precision = int(precision[1])
                    valueStr[1] = '%.*f' % (precision, valueStr[1])
                    if precision > 0 and trimTrailingZero:
                        valueStr[1] = valueStr[1].rstrip('0').rstrip('.')
                else:
                    valueStr[1] = self.format_as_fraction(
                        valueStr[1], maxDenominator = int(precision))
                valueStr = self.format_feet_inches(valueStr)
                
            else:
                if precision[0] == 'p':
                    precision = int(precision[1])
                else:
                    precision = 2
                    
                valueStr = '%.*f' % (precision, value)
                if precision > 0 and trimTrailingZero:
                    valueStr = valueStr.rstrip('0').rstrip('.')
                
                if unitSymbol and unit and unit != 'none':
                    if self.useLatex:
                        valueStr = '\SI{%s}{%s}' % (valueStr, unit)
                    else:
                        if unit == 'in':
                            unit = '"'
                        elif unit == 'ft':
                            unit = "'"
                        else:
                            unit = ' ' + unit                    
                        valueStr = valueStr + unit            


        ########################################
        # Start Drawing 
        ########################################
        group = self.createGroup(parent, label)

        # Draw Auxiliary Lines
        L1start = P1 + n_versor * self.auxLineOffset
        L2start = P2 + n_versor * self.auxLineOffset
        
        L1endRel = n_versor * (
            delta[0] + self.dimensionSpacing + self.auxLineExtension)
        L2endRel = n_versor * (
            delta[1] + self.dimensionSpacing + self.auxLineExtension)

        inkDraw.line.relCoords(group, [L1endRel.tolist()],
                               offset=L1start.tolist(),
                               lineStyle=self.auxiliaryLineStyle)
        inkDraw.line.relCoords(group, [L2endRel.tolist()],
                               offset=L2start.tolist(),
                               lineStyle=self.auxiliaryLineStyle)

        
        # Draw Dimension Line
        extraDist = 0
        if self.options.markerStyle == 'arrow':
            extraDist = t_versor * self.arrowSize

        Pstart = (L1start + L1endRel -
                  n_versor * (self.auxLineExtension) + extraDist)
        Pend = (L2start + L2endRel -
                n_versor * (self.auxLineExtension) - extraDist)
        
        if smallDimension:
            extraDist = t_versor * self.arrowSize
            Pstart -= extraDist
            Pend += extraDist
            arrowTailScale = 3
            PextStart =( Pstart - t_versor *
                         self.dimensionSpacing / arrowTailScale)
            PextEnd = (Pend + t_versor *
                       self.dimensionSpacing / arrowTailScale)

            inkDraw.line.absCoords(
                group, [PextStart.tolist(), Pstart.tolist()], offset=[0, 0],
                label='dim', lineStyle = self.ANGdimensionLineStyleSmall)
            inkDraw.line.absCoords(
                group, [PextEnd.tolist(), Pend.tolist()], offset=[0, 0],
                label='dim', lineStyle = self.ANGdimensionLineStyleSmall)
            
        else:
            Pstart += extraDist
            Pend -= extraDist
            inkDraw.line.absCoords(
                group, [Pstart.tolist(), Pend.tolist()], offset=[0, 0],
                label='dim', lineStyle=self.dimensionLineStyle)
            
            
        # Draw Dimension
        if valueStr == '':
            return group

        posDim = (Pstart + Pend) / 2.0
        # regular dimension style
        if not (smallDimension and value > 4 * self.fontSize):
            posDim += n_versor * self.textOffset

        # Keep text horizontal
        if horizontalText:
            textAngle = 0

            if smallDimension and value > 4 * self.fontSize: 
                justif = 'cc'

            else:  # regular dimension style
                if direction == 'parallel':
                    textSide = 1
                elif angle > 0:
                    textSide *= -1

                if angle <= 0 or angle == 180:
                    posDim += n_versor * self.fontSize
                
                if textSide * n_versor[0] < 0:
                    justif = 'cr'
                elif textSide * n_versor[0] > 0:
                    justif = 'cl'
                else:
                    justif = 'cc'

        # Rotated Text
        else:
            textAngle = (180 / math.pi) * math.atan2(-t_vector[1], t_vector[0])

            if abs(abs(angle + 45/2) - 90) <= 22.5:
                textAngle += 180
                textSide *= -1

            if abs(textAngle) == 180:
                textAngle = 0
                if abs(angle + 45) > 90:
                    textSide *= -1
                    
            if abs(textAngle) == 90:
                textAngle = 90
                textSide = 1 if angle > 0 else -1
            
            if textSide == -1:
                justif = 'tc'
            else:
                justif = 'bc'
                
            if smallDimension: 
                justif = 'cc'

        inkDraw.text.latex(self, group, valueStr, posDim,
                           fontSize = self.fontSize, refPoint=justif,
                           textColor = self.textColor,
                           LatexCommands=' ', angleDeg = textAngle)

        return group


    def getPointsLinDim(self, element):
        """ Extracts the 2 end points from the Obj.

        Also checks if distance is zero and reorder the points so that

          - if direction=='horizontal'  -> P1 is to the left
          - if direction=='vertical'  -> P1 is below
          - if direction=='parallel'  -> P1 is to the left. If line is vertical, ensures that P1 is below.

        :param element: element object
        :type element: element object
        :param direction: orientation of the dimension: horizontal, vertical, parallel
        :type direction: string


        :returns: [pointsList]

          - pointsList: list of points with the coordinates
        :rtype: list of list

        If the element does not have any transformation attribute, this function returns:
            transfAttrib=''
            transfMatrix=identity matrix

        **Example**

        >>> for id_elem,element in self.selected.iteritems():                # iterates through all selected elements
        >>>   pointsList = self.getPointsLinDim(self,element,'horizontal')
        """

        [P1, P2] = self.getPoints(element)

        t_vector = np.array(P2) - np.array(P1)
        angle = math.atan2(t_vector[1], t_vector[0]) * 180.0 / math.pi
        if angle < 0 or angle >= 180:
            temp = P1 
            P1 = P2
            P2 = temp

        return [P1, P2]


    def getPointsBB(self, element, direction, textSide):
        if len(element) == 0:
            element = [element]

        # Find the stroke width
        def getMaxStroke(e):
            w = 0
            for n in e:
                try:
                    style = simplestyle.parseStyle(n.get('style'))
                    strokeWidth = float(style['stroke-width']) * (style['stroke'] != 'none')
                except:
                    strokeWidth = 0
                w = max(strokeWidth, w)
                w = max(getMaxStroke(n), w)
            return w
                
        strokeWidth = getMaxStroke(element)

        
        P1 = simpletransform.computeBBox(element)
        if P1 is None:
            return None
        P2 = [P1[0] - strokeWidth / 2, P1[2] - strokeWidth / 2]
        P1 = [P1[1] + strokeWidth / 2, P1[3] + strokeWidth / 2]

        t_vector = np.array(P2) - np.array(P1)
        angle = math.atan2(t_vector[1], t_vector[0]) * 180.0 / math.pi
        if angle < 0 or angle >= 180:
            temp = P1 
            P1 = P2
            P2 = temp

        if direction == 'auto':
            x = abs(P1[0] - P2[0])
            y = abs(P1[1] - P2[1])
            direction = 'vertical' if y > x else 'horizontal'
                
        textSide = 1 if textSide == 'upperLeft' else -1        
        if direction == 'horizontal':
            p = textSide * min(textSide*P1[1], textSide*P2[1])
            P1[1] = P2[1] = p
        if direction == 'vertical':
            p = textSide * min(textSide*P1[0], textSide*P2[0])
            P1[0] = P2[0] = p

        return [P1, P2]


    def inches2ft(self, inches):
        return [int(inches / 12), inches % 12]


    def format_feet_inches(self, ft_inch, useShortUnit = True):
        if useShortUnit:
            ftUnit = "'"
            inchUnit = '"'
        else:
            ftUnit = "ft"
            inchUnit = 'in'

        if not isinstance(ft_inch, list):
            return str(ft_inch) + inchUnit

        ft = ''
        inch = ''
        if ft_inch[0] and ft_inch[0] != 0:
            ft = str(ft_inch[0]) + ftUnit
        if ft_inch[1] and ft_inch[1] != 0 and len(ft_inch[1]) > 0:
            inch = str(ft_inch[1]) + inchUnit

        if len(ft) > 0 and len(inch) > 0:
            ft = ft + ' '

        return ft + inch


    def format_as_fraction(self, x, maxDenominator = 16, delimiter = '-'):
        x = round(x * maxDenominator) / maxDenominator
        whole = int(x)
        if whole == 0:
            whole = ''
        else:
            whole = str(whole) 
        frac = x % 1
        if frac != 0:
            frac = frac.as_integer_ratio()
            frac = str(frac[0]) + '/' + str(frac[1])        
        else:
            frac = ''

        if len(whole) > 0 and len(frac) > 0:
            return whole + delimiter + frac
        elif len(whole) > 0:
            return whole
        else:
            return frac



if __name__ == '__main__':
    dimension = DimensionsLinear()
    dimension.affect()
