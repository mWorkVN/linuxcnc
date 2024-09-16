#!/usr/bin/env python3
#    Copyright 2007 John Kasunich and Jeff Epler
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from qtvcp.lib.qt_vismach.qt_vismach import *
import hal
import math

# no component made here - reads the pins directly
comp = None

# set measurement system
METRIC = 1
IMPERIAL = 25.4
MODEL_SCALING = METRIC

# parameters that define the geometry see scarakins.c for definitions these
# numbers match the defaults there, and will need to be changed or specified on
# the commandline if you are not using the defaults.
#setp scarakins.D1 400.0
#setp scarakins.D2 350.0
#setp scarakins.D3 -75.0
#setp scarakins.D4 350.0
##setp scarakins.D5 200.0
#setp scarakins.D6 0.0

d1 =  490.0
d2 =  340.0
d3 =   50.0
d4 =  250.0
d5 =   50.0
d6 =   50.0
j3min =  40.0
j3max = 270.0

# calculate a bunch of other dimensions that are used
# to scale the model of the machine
# most of these scale factors are arbitrary, to give
# a nicely proportioned machine.  If you know specifics
# for the machine you are modeling, feel free to change
# these numbers

tool_len = math.sqrt(d5*d5+d6*d6)    # don't change
tool_dia = tool_len / 6.0
# diameters of the arms
l1_dia = d2 / 5.0
l2_dia = d4 / 5.0
l3_dia = l2_dia * 0.8
# diameters of the "lumps" at the joints
j0_dia = l1_dia * 1.5
j1_dia = max(l1_dia * 1.25, l2_dia * 1.5)
j2_dia = l2_dia * 1.25

# other dims
j0_hi = l1_dia * 1.2
j1_hi1 = l1_dia * 1.1
j1_hi2 = l2_dia * 1.2
j2_hi = l2_dia * 1.3

# don't change these
tool_angle = math.degrees(math.atan2(d6,d5))
tool_radius = tool_dia / 2.0
l1_rad = l1_dia / 2.0
l2_rad = l2_dia / 2.0
l3_len = j3max + j2_hi * 0.7
l3_rad = l3_dia / 2.0
j0_hi = j0_hi / 2.0
j0_rad = j0_dia / 2.0
j1_hi1 = j1_hi1 / 2.0
j1_hi2 = j1_hi2 / 2.0
j1_rad = j1_dia / 2.0
j2_hi = j2_hi / 2.0
j2_rad = j2_dia / 2.0

size = max(d1+d3+l3_len,d2+d4+d6)

# tool - cylinder with a point, and a ball to hide the blunt back end
# the origin starts out at the tool tip, and we want to capture this
# "tooltip" coordinate system
tooltip = Capture()
# tool = Collection([
#     tooltip,
#     Sphere(0.0, 0.0, tool_len, tool_dia),
#     CylinderZ(tool_len, tool_radius, tool_dia, tool_radius),
#     CylinderZ(tool_dia, tool_radius, 0.0, 0.0)])
# tool = Translate([tool],0.0,0.0,-tool_len)    
# tool = Rotate([tool],tool_angle,0.0,-1.0,0.0)
# tool = HalRotate([tool],comp,"joint.3.pos-fb", 1, 0, 0, 1)
# outer arm
# start with link3 and the cylinder it slides in
tool = Collection([
    tooltip,
    CylinderZ(-j2_hi, j2_rad, j2_hi, j2_rad)])
# move to end of arm
tool = Translate([tool], d4*0.4, 0.0, 0.0)
# add the arm itself
tool = Collection([
    tool,
    CylinderX(d4*0.4, l2_rad, 1.5*j1_rad, l2_rad)])
# the joint gets interesting, because link2 can be above or below link1
if d3 > 0:
    flip = 1
else:
    flip = -1
# add the joint
tool = Collection([
    tool,
    Box(1.5*j1_rad, -0.9*j1_rad, -j1_hi2, 1.15*j1_rad, 0.9*j1_rad, j1_hi2),
    Box(1.15*j1_rad, -0.9*j1_rad, -0.4*d3, 0.0, 0.9*j1_rad, flip**2*j1_hi2),
    CylinderZ(-0.4*d3, j1_rad, flip*2*j1_hi2, j1_rad)])
# make the joint work
tool = HalRotate([tool],comp,"joint.3.pos-fb", 1, 0, 0, 1)



# start with link3 and the cylinder it slides in
link2 = Collection([
    tool,
    CylinderZ(-j2_hi, j2_rad, j2_hi, j2_rad)])
# move to end of arm
link2 = Translate([link2], d4, 0.0, 0.0)
# add the arm itself
link2 = Collection([
    link2,
    CylinderX(d4, l2_rad, 1.5*j1_rad, l2_rad)])
# the joint gets interesting, because link2 can be above or below link1

# add the joint
link2 = Collection([
    link2,
    Box(1.5*j1_rad, -0.9*j1_rad, -j1_hi2, 1.15*j1_rad, 0.9*j1_rad, j1_hi2),
    Box(1.15*j1_rad, -0.9*j1_rad, -0.4*d3, 0.0, 0.9*j1_rad, flip*j1_hi2),
    CylinderZ(-0.4*d3, j1_rad, flip*1.2*j1_hi2, j1_rad)])
# make the joint work
link2 = HalRotate([link2],comp,"joint.2.pos-fb", 1, 0, 0, 1)

###################################################

# inner arm
# the outer arm and the joint
link1 = Collection([
    Translate([link2],0.0,0.0,d3),
    #Box(-1.5*j1_rad, -0.9*j1_rad, -j1_hi1, -1.15*j1_rad, 0.9*j1_rad, j1_hi1),
    #Box(-1.15*j1_rad, -0.9*j1_rad, 0.4*d3, 0.0, 0.9*j1_rad, -flip*j1_hi1),
    CylinderZ(0.4*d3, j1_rad, flip*-1.2*j1_hi1, j1_rad),
    CylinderZ(0.6*d3, 0.8*j1_rad, 0.4*d3, 0.8*j1_rad)])
# move to end of arm
link1 = Translate([link1], d2, 0.0, 0.0)
# add the arm itself, and the inner joint
link1 = Collection([
    link1,
    CylinderX(d2-1.5*j1_rad, l1_rad, 1.5*j0_rad, l1_rad),
    Box(1.5*j0_rad, -0.9*j0_rad, -j0_hi, 0.0, 0.9*j0_rad, j0_hi),
    CylinderZ(-1.2*j0_hi, j0_rad, 1.2*j0_hi, j0_rad)])
# make the joint work
link1 = HalRotate([link1],comp,"joint.1.pos-fb", 1, 1, 0, 0)
link1 = Color([1, .5, .5, .5],[link1])
#stationary base
link0 = Collection([
    CylinderZ(d1-j0_hi, 0.8*j0_rad, d1-1.5*j0_hi, 0.8*j0_rad),
    CylinderZ(d1-1.5*j0_hi, 0.8*j0_rad, 0.07*d1, 1.3*j0_rad),
    CylinderZ(0.07*d1, 2.0*j0_rad, 0.0, 2.0*j0_rad)])
# slap the arm on top
link0 = Collection([
    link0,
    Translate([link1],0,0,d1)])


##############################################################




# # and a table for the workpiece - define in workpiece coords
reach = d2+d4-d6
table_height = d1+d3-j3max-d5

xbase = BoxCentered(1000, 200, 30)
# let's color it blue
xbase = Color([0, 0, 1, 1], [xbase])
# Move table so top is at zero for now,
# so work (default 0,0,0) is on top of table.
xbase = Translate([xbase], 0, 0, -15)

# group work and xbase together so they move together.
xassembly = Collection([link0,xbase])
# work is now defined and grouped, and default at 0,0,0, or
# currently on top of x part table.
# so we move table group upwards, taking work with it.
xassembly = Translate([xassembly], 0, 0, 35)

# Must define part motion before it becomes part of collection.
# Must have arguments, object itself, c (defined above), then finally scale from the pin to x y z.
# since this moves solely on X axis, only x is 1, rest is zero.
# you could use fractions for say axis that moves in compound like arm for example
# but this machine is very simple, so all axis will be purely full on axis and zero on other axis.
xassembly = HalTranslate([xassembly], None, "joint.0.pos-fb", 0, MODEL_SCALING, 0)
# # add a floor
floor = Box(-0.5*size,-0.5*size,-0.02*size,0.5*size,0.5*size,0.0)
work = Capture()
table = Collection([
    work,
    Box(-0.35*reach,-0.5*reach, -0.1*d1, 0.35*reach, 0.5*reach, 0.0)])
model = Collection([xassembly, floor,table])
#model = Collection([link4])

# show a title to prove the HUD
myhud = Hud()
myhud.show("Scara")

class Window(QWidget):

    def __init__(self,sizezoom):
        super(Window, self).__init__()
        self.glWidget = GLWidget()
        v = self.glWidget
        v.set_latitudelimits(-360, 360)
        size = max(d1+d3+l3_len,d2+d4+d6)

        v.hud = myhud
        v.hud.app = v #HUD needs to know where to draw

        world = Capture()
        v.model = Collection([model, world])
        v.distance = sizezoom
        v.near = size * 0.01
        v.far = size * 10.0
        v.tool2view = tooltip
        v.world2view = world
        v.work2view = work

        mainLayout = QHBoxLayout()
        mainLayout.setContentsMargins(0,0,0,0)
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)


# but it you call this directly it should work too

if __name__ == '__main__':
    main(model, tooltip, work , size=600, hud=myhud, lat=-75, lon=215)

