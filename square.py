from __future__ import division
from direct.showbase.ShowBase import ShowBase
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import GeomNode
from panda3d.core import LVector3
import random


def make_color_map(colors):
    # colors is a list that corresponds to (x, y, z) so
    # ('b', 'r') means blue varies with x, and red with y
    # this is a 2 dimensional space, so z corresponds to varies
    # with both x and y
    #
    # output is a dictionary, that shows mapping from x,y,z space to color space r,g,b
    # so, if we want (assuming above example input) x:b, y:r, z:None than our dictionary will
    # be 0:2, 1:0, 2:None
    # keys are x,y,x, values are r,g,b
    color_map = {0: None, 1: None, 2: None}
    # color_map = [None, None, None]
    for i, j in enumerate(colors):
        if j == 'r':
            color_map[i] = 0
        elif j == 'g':
            color_map[i] = 1
        elif j == 'b':
            color_map[i] = 2
    return color_map


# if setting the matching color manually,
# set colors to some combination of midpoint and static for starting position
# otherwise random and static
def set_start_position_colors(config=None):
    # will either be a random start or middle of field
    if config.get('match_direction') is None:
        print 'random'
        color_list = set_random_colors(config)
    else:
        print 'fixed'
        mid = config['c_range'][0] + (config['c_range'][1] - config['c_range'][0])/2
        color_list = [mid, mid, mid]
    color_list = fix_static_colors(config['colors'], config['static'], color_list)
    return color_list


# also use random for setting up match, if not fixed
# for setting up match, also want to specify which extreme to choose (left,right,front,back)
def set_match_colors(config, color_dict):
    # if not using fixed color, using random
    if config.get('match_direction') is None:
        color_list = set_random_colors(config)
    else:
        color_list = set_fixed_colors(config, color_dict)
    color_list = fix_static_colors(config['colors'], config['static'], color_list)
    return color_list


def set_random_colors(config):
    color_list = [random.uniform(config['c_range'][0], config['c_range'][1]) for i in range(3)]
    return color_list


def set_fixed_colors(config, color_dict):
    color_list = [None, None, None]
    # to make sure we have set the correct direction, corresponding directions available
    # only change to that direction, if we are using that axis.
    if config['colors'][0]:
        # print 'x direction'
        # print color_dict
        if any(d == 'right' for d in config['match_direction']):
            color_list[color_dict[0]] = config['c_range'][1]
        if any(d == 'left' for d in config['match_direction']):
            color_list[color_dict[0]] = config['c_range'][0]
    if len(config['colors']) > 1 and config['colors'][1]:
        if any(d == 'front' for d in config['match_direction']):
            color_list[color_dict[1]] = config['c_range'][0]
        if any(d == 'back' for d in config['match_direction']):
            color_list[color_dict[1]] = config['c_range'][1]
    # if things didn't match up, will have all Nones.
    if all([c is None for c in color_list]):
        raise NotImplementedError('a direction was not set')
    # if there are two directions, must be two matches
    print 'match', len(config['match_direction'])
    print 'colors', len(config['colors'])
    print config['colors']
    if len(config['match_direction']) != len(config['colors']):
        raise NotImplementedError('a direction was not set')

    return color_list


def fix_static_colors(colors, static, color_list):
    print 'fixed static'
    # finds color(s) that is/are not changing, and set
    # it equal to static. rest stay same.
    all_colors = ['r', 'g', 'b']
    for i, j in enumerate(all_colors):
        if j not in colors:
            color_list[i] = static
    return color_list


def setup_square(config):
    sq_colors = make_color_vertices(config)
    square = make_square(sq_colors)
    sq_node = GeomNode('square')
    sq_node.addGeom(square)
    return sq_node


def translate_color_map(config, color_dict, color_list):
    factor = 2 / (config['c_range'][1] - config['c_range'][0])
    translate = (config['c_range'][1] * factor) - 1
    last_avt = [0, 0]
    print 'translate this', color_list
    if color_dict[0] is not None:
        last_avt[0] = (color_list[color_dict[0]] * factor) - translate
    if color_dict[1] is not None:
        last_avt[1] = (color_list[color_dict[1]] * factor) - translate
    return last_avt, factor


# You can't normalize inline so this is a helper function
def normalized(*args):
    my_vec = LVector3(*args)
    my_vec.normalize()
    return my_vec


# helper function to make a square given the Lower-Left-Hand and
# Upper-Right-Hand corners
def make_square(sq_color):
    # sq_color is a list of tuples, describing each vertex:
    # (r, g, b, a) for [bl, br, tr, tl]
    x1 = -1
    y1 = -1
    z1 = -1
    x2 = 1
    y2 = -1
    z2 = 1
    v_format = GeomVertexFormat.getV3n3cpt2()
    v_data = GeomVertexData('square', v_format, Geom.UHDynamic)

    vertex = GeomVertexWriter(v_data, 'vertex')
    normal = GeomVertexWriter(v_data, 'normal')
    color = GeomVertexWriter(v_data, 'color')
    tex_coord = GeomVertexWriter(v_data, 'texcoord')

    # make sure we draw the sqaure in the right plane
    if x1 != x2:
        vertex.addData3(x1, y1, z1)
        vertex.addData3(x2, y1, z1)
        vertex.addData3(x2, y2, z2)
        vertex.addData3(x1, y2, z2)

        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
        normal.addData3(normalized(2 * x1 - 1, 2 * y2 - 1, 2 * z2 - 1))

    else:
        vertex.addData3(x1, y1, z1)
        vertex.addData3(x2, y2, z1)
        vertex.addData3(x2, y2, z2)
        vertex.addData3(x1, y1, z2)

        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z1 - 1))
        normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
        normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z2 - 1))

    # adding different colors to the vertex for visibility
    # color.addData4f(1.0, 0.0, 0.0, 1.0)
    # color.addData4f(0.0, 1.0, 0.0, 1.0)
    # color.addData4f(0.0, 0.0, 1.0, 1.0)
    # color.addData4f(1.0, 0.0, 1.0, 1.0)
    color.addData4f(sq_color[0])  # (0, 0) bottom left
    color.addData4f(sq_color[1])  # (0.5, 0) bottom right
    color.addData4f(sq_color[2])  # (0.5, 0.5) top right
    color.addData4f(sq_color[3])  # (0, 0.5) top left

    tex_coord.addData2f(0.0, 1.0)
    tex_coord.addData2f(0.0, 0.0)
    tex_coord.addData2f(1.0, 0.0)
    tex_coord.addData2f(1.0, 1.0)

    # Quads aren't directly supported by the Geom interface
    # you might be interested in the CardMaker class if you are
    # interested in rectangle though
    tris = GeomTriangles(Geom.UHDynamic)
    tris.addVertices(0, 1, 3)
    tris.addVertices(1, 2, 3)

    square = Geom(v_data)
    square.addPrimitive(tris)
    return square


# helper function to make the color vertices
def make_color_vertices(config):
    # make bottom left, right, top right, left
    # [(xmin, ymin), (xmax, ymin), (xmax, ymax), (ymax, xmin)]
    test = ['r', 'g', 'b']
    # append to the end to make sure we have 3 indices.
    colors = config['colors'][:]
    while len(colors) < 3:
        colors.append(None)
    # set the starting matrix with ones for everything, so don't have to worry about alpha
    color_vertices = [[1] * 4 for i in range(4)]
    for i in test:
        if i == colors[0]:
            # x coordinate
            color_vertices[0][test.index(i)] = config['c_range'][0]  # bottom left
            color_vertices[1][test.index(i)] = config['c_range'][1]  # bottom right
            color_vertices[2][test.index(i)] = config['c_range'][1]  # top right
            color_vertices[3][test.index(i)] = config['c_range'][0]  # top left
        elif i == colors[1]:
            # y coordinate
            color_vertices[0][test.index(i)] = config['c_range'][0]  # bottom left
            color_vertices[1][test.index(i)] = config['c_range'][0]  # bottom right
            color_vertices[2][test.index(i)] = config['c_range'][1]  # top right
            color_vertices[3][test.index(i)] = config['c_range'][1]  # top left
        elif i == colors[2]:
            # this definitely needs testing. not even sure what I want to happen here...
            # if I use the mid for bottom right and top left, I have something very similar
            # to what I have with two colors, the only difference is the bottom left corner
            mid = config['c_range'][0] + (config['c_range'][1] - config['c_range'][0])/2
            color_vertices[0][test.index(i)] = config['c_range'][1]  # bottom left
            color_vertices[1][test.index(i)] = mid  # bottom right
            color_vertices[2][test.index(i)] = config['c_range'][0]  # top right
            color_vertices[3][test.index(i)] = mid  # top left
            # color_vertices[0][test.index(i)] = config['c_range'][1]  # bottom left
            # color_vertices[1][test.index(i)] = config['c_range'][0]  # bottom right
            # color_vertices[2][test.index(i)] = config['c_range'][0]  # top right
            # color_vertices[3][test.index(i)] = config['c_range'][0]  # top left
        else:
            for j in range(4):
                color_vertices[j][test.index(i)] = config['static']
    # print 'what i did', color_vertices
    return [tuple(i) for i in color_vertices]


class ColorSquare(object):
    def __init__(self):
        self.base = ShowBase()
        self.base.disableMouse()
        self.base.camera.setPos(0, -10, 0)
        color_vertices = [(0.2, 0.2, 0.1, 1),
                          (0.2, 0.7, 0.1, 1),
                          (0.7, 0.7, 0.1, 1),
                          (0.7, 0.2, 0.1, 1)]
        square = make_square(color_vertices)
        sq_node = GeomNode('square')
        sq_node.addGeom(square)
        self.base.render.attachNewNode(sq_node)

if __name__ == "__main__":
    CS = ColorSquare()
    CS.base.run()