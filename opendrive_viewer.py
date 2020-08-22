#!/usr/bin/env python
# coding: utf-8

import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
import math
import sys
import os

class Line:
    def __init__(self):
        pass
    def setGeometry(self, s, x, y, hdg, length):
        self.s = s
        self.x = x
        self.y = y
        self.hdg = hdg
        self.length = length
    def setParamPoly3(self, aU, bU, cU, dU, aV, bV, cV, dV):
        self.aU = aU
        self.bU = bU
        self.cU = cU
        self.dU = dU
        self.aV = aV
        self.bV = bV
        self.cV = cV
        self.dV = dV
        
class Road:
    def __init__(self, name="", id="", junction = -1):
        self.name = name
        self.id = id
        self.junction = junction
        self.line = []
        self.pre = -1
        self.suc = -1
    def setRoad(self, name, id, junction):
        self.name = name
        self.id = id
        self.junction = junction
    def setPredecessor(self, pre):
        self.pre = pre
    def setSuccessor(self, suc):
        self.suc = suc
    

def rotation(x, t, x0 = np.array([0,0]), deg = False):
    x_ = x
    if deg == True:
        t = np.deg2rad(t)
    a = np.array([[np.cos(t), -np.sin(t)],
                  [np.sin(t),  np.cos(t)]])
    ax_ = np.dot(a, x_)
    ax = ax_ + x0
    return ax


def drawUV(aU, bU, cU, dU, aV, bV, cV, dV, length):
    U = []
    V = []
    p = 0.0
    dp = 0.2
    span = 0.0
    U_p = aU
    V_p = aV
    for i in range(6):
        p = i * dp
        U_ = aU + bU*p + cU*p**2 + dU*p**3
        V_ = aV + bV*p + cV*p**2 + dV*p**3
        U.append(U_)
        V.append(V_)
        U_p = U_
        V_p = V_
    return U, V
    
def convertUVtoXY(U, V, x, y, hdg):
    X0 = np.array([x, y])
    X = []
    Y = []
    for i in range(len(U)):
        xy = np.array([U[i], V[i]])
        XY_ = rotation(xy, hdg, X0)
        X.append(XY_[0])
        Y.append(XY_[1])
    return X, Y

class GUI:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
    def plotData(self, X, Y):
        plt.plot(X, Y, "-")
    def setLabel(self, label):
        self.label = label
    def setData(self, X, Y):
        self.sc = plt.scatter(X, Y, s=3)
    def setAnnotation(self):
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        self.annot.set_text("-")
    def update_annot(self, ind):
        i = ind["ind"][0]
        pos = self.sc.get_offsets()[i]
        self.annot.xy = pos
        text = self.label[i]
        self.annot.set_text(text)
    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            contain, ind = self.sc.contains(event)
            if contain:
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()
    def show(self):
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)
        plt.show()



def pickupRoadGeometry(child, road):
    if(child.tag == "road"):
        name = child.get('name')
        id = child.get('id')
        junction = child.get('junction')
        road_ = Road(name, id, junction)
        for child2 in child:
            if(child2.tag == "link"):
                for child3 in child2:
                    if(child3.tag == "predecessor"):
                        road_.setPredecessor(int(child3.get('elementId')))
                    if(child3.tag == "successor"):
                        road_.setSuccessor(int(child3.get('elementId')))
            if(child2.tag == "planView"):
                for child3 in child2:
                    if(child3.tag == "geometry"):
                        line_ = Line()
                        s = float(child3.get('s'))
                        x = float(child3.get('x'))
                        y = float(child3.get('y'))
                        hdg = float(child3.get('hdg'))
                        length = float(child3.get('length'))
                        line_.setGeometry(s, x, y, hdg, length)
                        for child4 in child3:
                            if(child4.tag == "line"):
                                aU = 0.0
                                bU = length
                                cU = 0.0
                                dU = 0.0
                                aV = 0.0
                                bV = 0.0
                                cV = 0.0
                                dV = 0.0
                                line_.setParamPoly3(aU, bU, cU, dU, aV, bV, cV, dV)
                                
                            if(child4.tag == "paramPoly3"):
                                aU = float(child4.get('aU'))
                                bU = float(child4.get('bU'))
                                cU = float(child4.get('cU'))
                                dU = float(child4.get('dU'))
                                aV = float(child4.get('aV'))
                                bV = float(child4.get('bV'))
                                cV = float(child4.get('cV'))
                                dV = float(child4.get('dV'))
                                line_.setParamPoly3(aU, bU, cU, dU, aV, bV, cV, dV)
                            if(child4.tag == "poly3"):
                                #TODO
                                print("Poly3 is not yet defined.")
                            if(child4.tag == "spiral"):
                                #TODO
                                print("Spiral is not yet defined.")
                            if(child4.tag == "arc"):
                                #TODO
                                print("Arc is not yet defined.")
                        road_.line.append(line_)
        road.append(road_)

def main(filename):
    if(os.path.exists(filename) == False):
        print("File does not exist")
        exit()
    gui = GUI()
    tree = ET.parse(filename)
    root = tree.getroot()
    road = []
    # get necessary information from .xodr and put it on the road[]
    for child in root:
        pickupRoadGeometry(child, road)
    
    # convert road to points
    X_all = []
    Y_all = []
    label_all = []
    for i in range(len(road)):
        for j in range(len(road[i].line)):
            x = road[i].line[j].x
            y = road[i].line[j].y
            hdg = road[i].line[j].hdg
            length = road[i].line[j].length
            aU = road[i].line[j].aU
            bU = road[i].line[j].bU
            cU = road[i].line[j].cU
            dU = road[i].line[j].dU
            aV = road[i].line[j].aV
            bV = road[i].line[j].bV
            cV = road[i].line[j].cV
            dV = road[i].line[j].dV
            U, V = drawUV(aU, bU, cU, dU, aV, bV, cV, dV, length)
            X, Y = convertUVtoXY(U, V, x, y, hdg)
            # display points
            gui.plotData(X, Y)
            for k in range(len(X)):
                label_all.append(str(road[i].name)+":"+str(road[i].id))
            X_all.append(X)
            Y_all.append(Y)
    
    # display road positions and labels
    gui.setData(X_all, Y_all)
    gui.setLabel(label_all)
    gui.setAnnotation()
    gui.show()


if __name__ == "__main__":
    if(len(sys.argv)<2):
        print("Please specify an OpenDrive file.")
        exit()
    main(sys.argv[1])
