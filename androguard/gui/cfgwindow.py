import hashlib
import pydot
import svgutils
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QScrollArea, QWidget
from PyQt5.QtCore import Qt
from androguard.gui.xrefwindow import XrefDialogString
from androguard.core.bytecode import method2dot

class CfgWindow(QtWidgets.QWidget):
    def __init__(self,
                 win=None,
                 current_class=None,
                 class_analysis=None):
        super().__init__(win)

        self.mainwin = win
        self.title = current_class.current_title
        self.current_class = current_class
        self.class_analysis = class_analysis

        # wrapper widget for scrolling
        scrollWidget = QWidget()
        # layout for the scroll widget
        layout = QVBoxLayout(self)

        # create graphs for every method
        svgs = self.get_method_graphs()
        for i, svg in enumerate(svgs):
            # use svgutils to get the SVG size attributes
            svgParsed = svgutils.transform.fromstring(svg.decode('utf-8'))
            svgWidget = CfgSVGWindow(svg, win)
            # height and length are of the format "12pt" hence the [:-2]
            svgWidget.setFixedHeight(int(svgParsed.height[:-2])*1.5)
            svgWidget.setFixedWidth(int(svgParsed.width[:-2])*1.5)
            layout.addWidget(svgWidget)

        # apply layout to wrapper widget
        scrollWidget.setLayout(layout)

        # define a scroll area to actually make the widget scrollable
        scrollArea = QScrollArea()
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollArea.setWidgetResizable(False)
        # set scroll widget to scroll area
        scrollArea.setWidget(scrollWidget)

        # create a vbox layout and add scroll area
        vBoxLayout = QVBoxLayout(self)
        vBoxLayout.addWidget(scrollArea)
        # apply the layout to this widget
        self.setLayout(vBoxLayout)

    def get_method_graphs(self):
        # get _the_ androguard ``Analysis`` object that contains our current class
        dx = self.mainwin.session.get_analysis(self.current_class)
        # we're going to fill this svgs array with one svg graph per method
        svgs = []
        # m is of type ``EncodedMethod```
        for m in self.current_class.get_methods():
            # get a ``MethodAnalysis`` object for our method m
            mx = dx.get_method(m)
            # get a graph of our method in dot format
            buff_dot = method2dot(mx)
            # unpack the returned graph list because we expect a single graph
            (graph,) = self.create_graph(buff_dot, str(m.get_name()))
            # render svg
            svg = graph.create_svg()
            svgs.append(svg)

        return svgs


    def create_graph(self, data, name):
        """
        Constructs an actual CFG from dot output of method2dot and loads it with pydot

        :param data: :string:
        :param colors: dict of colors to use, if colors is None the default colors are used

        :returns: pydot CFG
        :rtype: class: ``pydot.Dot``
        """
        # this is from the bytecode.py
        # pydot is optional!
        import pydot

        buff = "digraph {\n"
        buff += "graph [rankdir=TB]\n"
        buff += "node [shape=plaintext]\n"

        # subgraphs cluster
        buff += "subgraph cluster_{} ".format(hashlib.md5(bytearray(name, "UTF-8")).hexdigest())
        buff += "{\n"
        buff += "label=\"{}\"\n".format(data['name'])
        buff += data['nodes']
        buff += "}\n"

        # subgraphs edges
        buff += data['edges']
        buff += "}\n"

        graph = pydot.graph_from_dot_data(buff)

        return graph

class CfgSVGWindow(QtSvg.QSvgWidget):
    def __init__(self, svg, win=None):
        super().__init__(win)
        self.mainwin = win
        self.title = "CFG"
        self.load(svg)