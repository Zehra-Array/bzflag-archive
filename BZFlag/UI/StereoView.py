""" BZFlag.UI.StereoView

A 3d scene renderer that does side-by-side 2-channel stereo (usually for SGI
visualization hardware)
"""
#
# Python BZFlag Protocol Package
# Copyright (C) 2003 Micah Dowty <micahjd@users.sourceforge.net>
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from BZFlag.UI import Viewport, ThreeDView, ThreeDControl, ThreeDRender, Layout, HUD
import BZFlag
from OpenGL.GL import *

class StereoView:
    """Shows a side-by-side stereo view of the BZFlag game, renderable
       to an OpenGLViewport.
       """
    def __init__(self, game, viewport):
        lefteye  = ThreeDView.ThreeDView(game, viewport.region(Layout.Rect(viewport).left(0.5)))
        righteye = ThreeDView.ThreeDView(game, viewport.region(Layout.Rect(viewport).right(0.5)))
        ThreeDControl.Viewing(lefteye, viewport)
        righteye.camera = lefteye.camera

    def render(self):
        eyesep = 12.5
        angle = math.atan(eyesep / self.camera.distance)
        # draw left eye
        lefteye.camera.azimuthOffset = -angle
        lefteye.render()
        # draw right eye
        righteye.camera.azimuthOffset = angle
        righteye.render()

def attach(game, eventLoop):
    viewport = Viewport.OpenGLViewport(eventLoop, (1600, 600))
    view = StereoView(game, viewport)
    return viewport
