""" BZFlag.UI.Viewport.OpenGL

A Viewport implementation for OpenGL. This uses Pygame to set up an OpenGL
context and receive events, hence this is a subclass of the Pygame viewport.
On top of PygameViewport, this class manages viewport-wide OpenGL context
details like field of view, clearing the color and Z buffers, and wireframe mode.

When should a feature go in the Viewport rather than in something like ThreeDRender?
If the feature should affect sub-viewports created by region(), or it's important
that it only ever be invoked once per frame, it might be a good cantidate to go here.
"""
#
# Python BZFlag Package
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

from __future__ import division
from Pygame import PygameViewport
from OpenGL.GL import *
from OpenGL.GLU import *
from BZFlag.UI import GLExtension
from BZFlag import Event
import pygame, copy


class OpenGLViewport(PygameViewport):
    """Subclasses PygameView to provide OpenGL initialization"""
    def init(self):
        # Test for OpenGL extensions we can use
        GLExtension.test()

        self.nearClip    = 0.1
        self.farClip     = 2500.0
        self.fov         = 45.0
        self.rectExp     = [0,0] + list(self.size)  # A function or list specifying our relative viewport
        self.rect        = self.rectExp             # Our absolute viewport

        # Set up some common OpenGL defaults
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glShadeModel(GL_SMOOTH)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        # Set up the Mode object that handles viewport-wide per-frame modes.
        # By default we use ClearedMode.
        self.mode = ClearedMode()
        self.onSetupFrame.observe(lambda: self.mode.setupFrame())

        def onResize():
            self.rectExp = [0,0] + list(self.size)
        self.onResize.observe(onResize)

        self.onSetupFrame.observe(self.configureOpenGL)

    def onFinishFrame(self):
        self.mode.finishFrame()
        PygameViewport.onFinishFrame(self)

    def evalViewport(self):
        """Evaluate our viewport if necessary, and set up our 'size' and 'viewport' members"""
        if callable(self.rectExp):
            v = self.rectExp()
        else:
            v = self.rectExp
        if self.parent:
            v = (v[0] + self.parent.rect[0],
                 v[1] + self.parent.rect[1],
                 v[2], v[3])
        self.rect = v
        self.size = v[2:]

    def configureOpenGL(self):
        glViewport(*self.rect)

        # Set up the projection matrix with the current viewport size and FOV.
        # If we have no FOV, set up an orthogonal mode scaled in pixels.
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.setProjectionMatrix()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDepthRange(0.01,2000)

    def setProjectionMatrix(self):
        if self.fov:
            gluPerspective(self.fov, float(self.size[0]) / self.size[1], self.nearClip, self.farClip)
        else:
            glOrtho(0,self.size[0],self.size[1],0, -self.farClip, self.farClip)

    def getModeFlags(self):
        return PygameViewport.getModeFlags(self) | pygame.OPENGL

    def resize(self, size):
        """Before setting our display mode, set up any OpenGL attributes we need"""
        self.setGLAttributes()
        PygameViewport.resize(self, size)

    def setGLAttributes(self):
        """A hook allowing subclasses the ability to set OpenGL attributes before initializing the context"""
        pass

    def render(self):
        """Reevaluate our viewport, then do the usual rendering sequence"""
        self.evalViewport()
        PygameViewport.render(self)

    def region(self, rect, renderLink='after'):
        """Return a class that represents a rectangular subsection of this viewport.
           To maintain something resembling OpenGL state integrity, it disconnects
           the region's rendering events from ours and appends them to our rendering
           sequence.

           In addition to a rectangle, this function can accept a function that
           will be lazily evaluated to a rectangle each frame. This makes it possible
           to create regions with animated or dynamically sized positions.

           renderLink controls how this region is linked into its parent's rendering
           sequence. 'after' inserts it after all other entries, 'before' before all
           others, None doesn't insert it.
           """
        sub = copy.copy(self)
        sub.parent = self
        sub.rectExp = rect
        sub.onSetupFrame  = Event.Event(sub.configureOpenGL)
        sub.onDrawFrame   = Event.Event()
        sub.onFinishFrame = Event.Event()
        sub.renderSequence = [sub.onSetupFrame,
                              sub.onDrawFrame,
                              sub.onFinishFrame]

        if renderLink == 'after':
            # Stick it in our render sequence right before our onFinishFrame which flips the buffer
            # This should be safe for nesting viewport regions-  and the last entry will always be
            # the root viewport's onFinishFrame event.
            self.rootView.renderSequence = self.rootView.renderSequence[:-1] + \
                                           [sub.render] + \
                                           self.rootView.renderSequence[-1:]

        if renderLink == 'before':
            self.rootView.renderSequence = [sub.render] + self.rootView.renderSequence

        # Ignore the caption on sub-viewports
        sub.setCaption = lambda title: None
        return sub


class StereoGLViewport(OpenGLViewport):
    """An OpenGLViewport subclass that uses a stereo OpenGL context, for
       big expensive hardware designed for stereo rendering :)
       """
    def setGLAttributes(self):
	pygame.display.gl_set_attribute(pygame.GL_STEREO, 1)


class ViewportMode:
    """Abstract base class for a mode that affects the rendering
       initialization and completion of an entire viewport.
       """
    clearBuffers = GL_DEPTH_BUFFER_BIT
    
    def __init__(self):
        if self.__class__ == ViewportMode:
            raise Exception("ViewportMode is an abstract base class and cannot be instantiated")
    
    def setupFrame(self):
        """Called during the viewport's onSetupFrame event"""
        if self.clearBuffers:
            glClear(self.clearBuffers)

    def finishFrame(self):
        """Called during the viewport's onFinishFrame event, before the page flip"""
        pass


class UnclearedMode(ViewportMode):
    """A viewport mode in which the color buffer is not cleared
       each frame, but the depth buffer is still cleared.
       This happens to be the default.
       """
    pass


class ClearedMode(ViewportMode):
    """A viewport mode in which the color buffer is cleared each frame"""
    clearBuffers = ViewportMode.clearBuffers | GL_COLOR_BUFFER_BIT
    
    def __init__(self, clearColor=(0,0,0,1)):
        self.clearColor = clearColor

    def setupFrame(self):
        glClearColor(*self.clearColor)
        ViewportMode.setupFrame(self)


class WireframeMode(ClearedMode):
    """A viewport mode that draws all polygons in wireframe, with
       a different clear color that makes them stand out better.
       """
    def __init__(self, clearColor=(0.5, 0.5, 0.5, 1)):
        ClearedMode.__init__(self, clearColor)

    def setupFrame(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
        ClearedMode.setupFrame(self)

    def finishFrame(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);


class XRayMode(ClearedMode):
    """A viewport mode that annotates the scene with information about it's depth complexity.
       More opaque shading indicates more pixels have been rendered at that location,
       with overlaid numbers indicating exactly how many. The name 'X-Ray Mode' comes
       from it's ability to see through objects, visually representing their density.
       """
    clearBuffers = ClearedMode.clearBuffers | GL_STENCIL_BUFFER_BIT
    
    def __init__(self, clearColor=(0,0,0,1), xRayColor=(1, 0, 0, 0.8), depthRange=10):
        ClearedMode.__init__(self, clearColor)
        self.xRayColor = xRayColor
        self.depthRange = range(depthRange)

        # Render number textures we'll use to indicate each depth range.
        # This uses the lower-level FontPage class from GLText to render
        # each number to a different texture, for tiling fun.

        self.fontName = 'VeraBd.ttf'
        self.fontSize = 12
        self.texSize = 16
        self.texRepeats = (glGetIntegerv(GL_VIEWPORT)[2] / self.texSize,
                           glGetIntegerv(GL_VIEWPORT)[3] / self.texSize)
                           
        from BZFlag.UI import GLText
        self.depthTextures = {}
        font = GLText.Font(self.fontName, [self.fontSize]).findRendered(self.fontSize).font
        for depth in self.depthRange:
            page = GLText.FontPage(font, (self.texSize, self.texSize))
            s = str(depth)
            if depth == self.depthRange[-1]:
                s += "!"
            page.pack(s)
            page.updateTexture()
            self.depthTextures[depth] = page.texture

    def setupFrame(self):
        """Every time a pixel is drawn, increment the stencil buffer"""
        glEnable(GL_STENCIL_TEST)
        glClearStencil(0)
        ClearedMode.setupFrame(self)
        glStencilFunc(GL_ALWAYS, 0, 0xFF)
        glStencilOp(GL_KEEP, GL_INCR, GL_INCR)

    def finishFrame(self):
        """Render several rectangles over the scene, each testing against
           a different value of the stencil buffer and drawn using a
           corresponding alpha component in its color.
           """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)

        for value in self.depthRange:
            # Each iteration we draw over the areas with one particular depth complexity
            if value == self.depthRange[-1]:
                glStencilFunc(GL_LEQUAL, value, 0xFF)
            else:
                glStencilFunc(GL_EQUAL, value, 0xFF)

            # Color with alpha corresponding to depth
            unitDepth = float(value) / self.depthRange[-1]            
            glColor4f(self.xRayColor[0],
                      self.xRayColor[1],
                      self.xRayColor[2],
                      self.xRayColor[3] * unitDepth)
            glRectf(-1, -1, 1, 1)

            # Texture to numerically indicate depth
            self.depthTextures[value].bind()            
            glEnable(GL_TEXTURE_2D)
            glColor4f(1,1,1,0.35)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0)
            glVertex2f(-1, -1)
            glTexCoord2f(self.texRepeats[0], 0)
            glVertex2f(1, -1)
            glTexCoord2f(*self.texRepeats)
            glVertex2f(1, 1)
            glTexCoord2f(0, self.texRepeats[1])
            glVertex2f(-1, 1)
            glEnd()
            glDisable(GL_TEXTURE_2D)
        glDisable(GL_STENCIL_TEST)

### The End ###