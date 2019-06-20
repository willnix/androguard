import hashlib
import pydot
import svgutils
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QScrollArea
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

        #Container Widget
        widget = QtWidgets.QWidget()
        #Layout of Container Widget
        layout = QVBoxLayout(self)

        # create graphs for every method
        svgs = self.get_method_graphs()
        for i, svg in enumerate(svgs):
            svgParsed = svgutils.transform.fromstring(svg.decode('utf-8'))
            svgWidget = CfgSVGWindow(svg, win)
            svgWidget.setFixedHeight(int(svgParsed.height[:-2]))
            svgWidget.setFixedWidth(int(svgParsed.width[:-2]))
            layout.addWidget(svgWidget)
        # set layout to container widget
        widget.setLayout(layout)

        #Scroll Area Properties
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(False)
        scroll.setWidget(widget)

        #Scroll Area Layer add
        vLayout = QVBoxLayout(self)
        vLayout.addWidget(scroll)
        self.setLayout(vLayout)

    def get_method_graphs(self):
        dx = self.mainwin.session.get_analysis(self.current_class)

        svgs = []
        for m in self.current_class.get_methods():
            mx = dx.get_method(m)
            buff_dot = method2dot(mx)
            # unpack the returned graph list because we expect a single graph
            (graph,) = self.create_graph(buff_dot, "png")
            svg = graph.create_svg()
            svgs.append(svg)

        return svgs


    def create_graph(self, data, output):
        # this is from the androguard source
        buff = "digraph {\n"
        buff += "graph [rankdir=TB]\n"
        buff += "node [shape=plaintext]\n"

        # subgraphs cluster
        buff += "subgraph cluster_" + hashlib.md5(output.encode('utf-8')).hexdigest() + " {\nlabel=\"%s\"\n" % data['name']
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