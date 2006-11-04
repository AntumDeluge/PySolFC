## vim:ts=4:et:nowrap
##
##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## Copyright (C) 2003 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2002 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2001 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 2000 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1999 Markus Franz Xaver Johannes Oberhumer
## Copyright (C) 1998 Markus Franz Xaver Johannes Oberhumer
## All Rights Reserved.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
## Markus F.X.J. Oberhumer
## <markus@oberhumer.com>
## http://www.oberhumer.com/pysol
##
##---------------------------------------------------------------------------##

__all__ = ['SelectDialogTreeData']

# imports
import os, re, sys, types
import Tile as Tkinter
import tkFont

# PySol imports
from pysollib.mfxutil import destruct, Struct, KwStruct, kwdefault

# Toolkit imports
from tkutil import makeImage
from tkcanvas import MfxCanvas
from tktree import MfxTreeLeaf, MfxTreeNode, MfxTreeInCanvas


# /***********************************************************************
# // Nodes
# ************************************************************************/

class SelectDialogTreeLeaf(MfxTreeLeaf):
    def drawSymbol(self, x, y, **kw):
        if self.tree.nodes.get(self.symbol_id) is not self:
            self.symbol_id = self.tree.canvas.create_image(x, y,
                image=self.tree.data.img[2+(self.key is None)], anchor="nw")
            self.tree.nodes[self.symbol_id] = self


class SelectDialogTreeNode(MfxTreeNode):
    def __init__(self, tree, text, select_func, expanded=0, parent_node=None):
        MfxTreeNode.__init__(self, tree, parent_node, text, key=None, expanded=expanded)
        # callable or a tuple/list of MfxTreeNodes
        self.select_func = select_func

    def drawSymbol(self, x, y, **kw):
        if self.tree.nodes.get(self.symbol_id) is not self:
            self.symbol_id = self.tree.canvas.create_image(x, y,
                image=self.tree.data.img[self.expanded], anchor="nw")
            self.tree.nodes[self.symbol_id] = self

    def getContents(self):
        # cached values
        if self.subnodes is not None:
            return self.subnodes
        ##print self.whoami()
        if type(self.select_func) in (types.TupleType, types.ListType):
            return self.select_func
        return self._getContents()

    def _getContents(self):
        # subclass
        return []


# /***********************************************************************
# // Tree database
# ************************************************************************/

class SelectDialogTreeData:
    img = []  # loaded in Application.loadImages3
    def __init__(self):
        self.tree_xview = (0.0, 1.0)
        self.tree_yview = (0.0, 1.0)


# /***********************************************************************
# // Canvas that shows the tree (left side)
# ************************************************************************/

class SelectDialogTreeCanvas(MfxTreeInCanvas):
    def __init__(self, dialog, parent, key, default,
                 font=None, width=-1, height=-1, hbar=2, vbar=3):
        self.dialog = dialog
        self.default = default
        self.n_selections = 0
        self.n_expansions = 0
        #
        disty = 16
        if width < 0:
            width = 400
        if height < 0:
            height = 20 * disty
            if parent and parent.winfo_screenheight() >= 600:
                height = 25 * disty
            if parent and parent.winfo_screenheight() >= 800:
                height = 30 * disty
        self.lines = height / disty
        MfxTreeInCanvas.__init__(self, parent, self.data.rootnodes,
                                 width=width, height=height,
                                 hbar=hbar, vbar=vbar)
        self.style.distx = 20
        self.style.disty = disty
        self.style.width = 16     # width of symbol
        self.style.height = 14    # height of symbol
        if font:
            self.style.font = font
            f = tkFont.Font(parent, font)
            h = f.metrics()["linespace"]
            self.style.disty = max(self.style.width, h)

        self.draw()
        self.updateSelection(key)
        if self.hbar:
            ##print self.data.tree_yview
            ##print self.canvas.xview()
            self.canvas.xview_moveto(self.data.tree_xview[0])
        if self.vbar:
            ##print self.data.tree_yview
            ##print self.canvas.yview()
            self.canvas.yview_moveto(self.data.tree_yview[0])

    def destroy(self):
        if self.n_expansions > 0:   # must save updated xyview
            self.data.tree_xview = self.canvas.xview()
            self.data.tree_yview = self.canvas.yview()
        MfxTreeInCanvas.destroy(self)

    def getContents(self, node):
        return node.getContents()

    def singleClick(self, event=None):
        node = self.findNode()
        if isinstance(node, MfxTreeLeaf):
            if not node.selected and node.key is not None:
                oldcur = self.canvas["cursor"]
                self.canvas["cursor"] = "watch"
                self.canvas.update_idletasks()
                self.n_selections = self.n_selections + 1
                self.updateSelection(node.key)
                self.dialog.updatePreview(self.selection_key)
                self.canvas["cursor"] = oldcur
        elif isinstance(node, MfxTreeNode):
            self.n_expansions = self.n_expansions + 1
            node.expanded = not node.expanded
            self.redraw()
        return "break"

    def doubleClick(self, event=None):
        node = self.findNode()
        if isinstance(node, MfxTreeLeaf):
            if node.key is not None:
                self.n_selections = self.n_selections + 1
                self.updateSelection(node.key)
                self.dialog.mDone(self.default)
        elif isinstance(node, MfxTreeNode):
            self.n_expansions = self.n_expansions + 1
            node.expanded = not node.expanded
            self.redraw()
        return "break"
