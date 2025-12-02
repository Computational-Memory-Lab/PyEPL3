#!/usr/bin/python

from pyepl.locals import *
	
class TextPool2(TextPool):
    """
    Pool subclass for text.
    """
    def __init__(self, fileordir, size=None, color=None, font=None, *tdicts, **ddicts):
        """
        Constructor assumes it will at least receive a directory from
        which to load images, and optionally scale factor(s) to apply
        to all images in the directory.
        """
        list.__init__(self)
        self.loadFromSourcePath(fileordir, size, color, font)
        for d in tdicts:
            list.append(self, PoolDict(d))
        for name, d in ddicts.iteritems():
            d = PoolDict(d)
            d.name = name
            list.append(self, d)
    def isInPool(self, **attrvalues):
        """
        New attribute of TextPool2! -- Chris
	Outputs the index number of the word given. If the word is not in
	the pool it will output "-1".
        """
        try:
            return self.index(self.iterFindBy(**attrvalues).next())
        except StopIteration:
            return -1
