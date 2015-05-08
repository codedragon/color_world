from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Camera, NodePath
from panda3d.core import GeomNode
from square import make_square, make_color_vertices


class ColorMaps(object):
    def __init__(self):
        self.base = ShowBase()
        self.base.disableMouse()
        self.base.camera.setPos(0, -5, 0)
        config = {'colors': ['r', 'g'],
                  'variance': [0.1, 0.6],
                  'static': 0.1}
        color_vertices = make_color_vertices(config)
        # print color_vertices
        square = make_square(color_vertices)
        sq_node = GeomNode('square')
        sq_node.addGeom(square)
        self.base.render.attach_new_node(sq_node)
        configs = []
        configs.append({'colors': ['g', 'b'],
                       'variance': [0.1, 0.6],
                       'static': 0.1})
        configs.append({'colors': ['r', 'b'],
                       'variance': [0.1, 0.6],
                       'static': 0.1})
        configs.append({'colors': ['r', 'b'],
                       'variance': [0.4, 0.9],
                       'static': 0.1})
        configs.append({'colors': ['r', 'b'],
                       'variance': [0.1, 0.6],
                       'static': 0.3})
        configs.append({'colors': ['r', 'b'],
                       'variance': [0.1, 0.6],
                       'static': 0.5})
        configs.append({'colors': ['r', 'b'],
                       'variance': [0.1, 0.6],
                       'static': 0.7})
        configs.append({'colors': ['r', 'b'],
                       'variance': [0.1, 0.6],
                       'static': 0.9})
        configs.append({'colors': ['r', 'g'],
                       'variance': [0.1, 0.6],
                       'static': 0.1})
        configs.append({'colors': ['r', 'g'],
                       'variance': [0.1, 0.6],
                       'static': 0.3})
        configs.append({'colors': ['r', 'g'],
                       'variance': [0.1, 0.6],
                       'static': 0.5})
        configs.append({'colors': ['r', 'g'],
                       'variance': [0.1, 0.6],
                       'static': 0.7})
        configs.append({'colors': ['r', 'g'],
                       'variance': [0.0, 0.6],
                       'static': 0.9})
        configs.append({'colors': ['b', 'r', 'g'],
                       'variance': [0.1, 0.6],
                       'static': 0.7})
        configs.append({'colors': ['b', 'g', 'r'],
                       'variance': [0.1, 0.6],
                       'static': 0.9})
        configs.append({'colors': ['r', 'g', 'b'],
                       'variance': [0.1, 0.6],
                       'static': 0.9})
        cams = [self.base.cam]
        for config in configs:
            cams.append(self.make_new_region(config))
        self.split_screen(*cams)

    def make_new_region(self, config):
        new_dr = self.base.win.makeDisplayRegion(0, 0.25, 0.75, 1)
        new_render = NodePath('new_render')  # the string parameter is important
        new_cam = new_render.attach_new_node(Camera('new_cam'))
        new_cam.setPos(0, -5, 0)
        new_dr.setCamera(new_cam)
        color_vertices = make_color_vertices(config)
        square = make_square(color_vertices)
        sq_node = GeomNode('square')
        sq_node.addGeom(square)
        new_render.attach_new_node(sq_node)
        return new_cam

    def split_screen(self, *args):
        drs = []
        for i, j in enumerate(args):
            print i, j
            drs.append(j.node().getDisplayRegion(0))
            j.node().getLens().setAspectRatio(float(drs[i].getPixelWidth()) / float(drs[i].getPixelHeight()))
        if len(drs) == 4:
            drs[0].setDimensions(0, 0.5, 0, 0.5)
            drs[1].setDimensions(0.5, 1, 0, 0.5)
            drs[2].setDimensions(0, 0.5, 0.5, 1)
            drs[3].setDimensions(0.5, 1, 0.5, 1)
        elif len(drs) == 16:
            drs[0].setDimensions(0, 0.25, 0, 0.25)
            drs[1].setDimensions(0.25, 0.5, 0, 0.25)
            drs[2].setDimensions(0.5, 0.75, 0, 0.25)
            drs[3].setDimensions(0.75, 1, 0, 0.25)
            drs[4].setDimensions(0, 0.25, 0.25, 0.5)
            drs[5].setDimensions(0.25, 0.5, 0.25, 0.5)
            drs[6].setDimensions(0.5, 0.75, 0.25, 0.5)
            drs[7].setDimensions(0.75, 1, 0.25, 0.5)
            drs[8].setDimensions(0, 0.25, 0.5, 0.75)
            drs[9].setDimensions(0.25, 0.5, 0.5, 0.75)
            drs[10].setDimensions(0.5, 0.75, 0.5, 0.75)
            drs[11].setDimensions(0.75, 1, 0.5, 0.75)
            drs[12].setDimensions(0, 0.25, 0.75, 1)
            drs[13].setDimensions(0.25, 0.5, 0.75, 1)
            drs[14].setDimensions(0.5, 0.75, 0.75, 1)
            drs[15].setDimensions(0.75, 1, 0.75, 1)

if __name__ == "__main__":
    CM = ColorMaps()
    CM.base.run()
