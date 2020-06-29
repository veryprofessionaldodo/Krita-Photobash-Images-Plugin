from krita import *
from . import *

Krita.instance().addDockWidgetFactory(DockWidgetFactory("PhotobashDocker", DockWidgetFactoryBase.DockRight, PhotobashDocker))