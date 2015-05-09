import unittest
import square
import color_world as cw
from panda3d.core import loadPrcFileData, LVector3


class ColorWorldTests(unittest.TestCase):

    def test_make_color_map(self):
        colors = ['r', 'b']
        color_map = square.make_color_map(colors)
        # mapping, x, y, z, r is 0, g is 1, b is 2
        known = {0: 0, 1: 2, 2: None}
        self.assertEqual(color_map, known)

    def test_make_color_map_with_z(self):
        colors = ['r', 'b', 'g']
        color_map = square.make_color_map(colors)
        known = {0: 0, 1: 2, 2: 1}
        self.assertEqual(color_map, known)

    def test_make_color_map_with_new_order(self):
        colors = ['g', 'b', 'r']
        color_map = square.make_color_map(colors)
        known = {0: 1, 1: 2, 2: 0}
        self.assertEqual(color_map, known)

    def test_make_color_vertices(self):
        config = {'colors': ['g', 'r'],
                  'variance': [0.2, 0.7],
                  'static': 0.1}
        # green on x axis, red on y axis, blue static
        color_vertices = square.make_color_vertices(config)
        known = [(0.2, 0.2, 0.1, 1),
                 (0.2, 0.7, 0.1, 1),
                 (0.7, 0.7, 0.1, 1),
                 (0.7, 0.2, 0.1, 1)]
        self.assertEqual(color_vertices, known)

    def test_starting_colors(self):
        config = {'colors': ['b', 'r'],
                  'variance': [0.2, 0.7],
                  'static': 0.1}
        color_list = square.set_start_colors(config)
        mid = config['variance'][0] + (config['variance'][1] - config['variance'][0])/2
        self.assertEqual([mid, 0.1, mid], color_list)

    def test_change_background(self):
        config = {'colors': ['g', 'r'],
                  'variance': [0.2, 0.7],
                  'static': 0.1,
                  'win': False}
        loadPrcFileData("", "window-type offscreen")
        test_cw = cw.ColorWorld(config)
        # force some variables to be what we want them to be.
        test_cw.color_list = [0.5, 0.5, 0.5]
        new_color = test_cw.color_list
        # x, y, z; r, g, b
        # {x: r, y: b, z: None} corresponds to {0: 0, 1: 2, 2: None}
        test_cw.color_dict = {0: 0, 1: 2, 2: None}
        move = LVector3(0.1, 0, 0)
        stop = test_cw.change_background(move)
        new_color[0] = 0.5 + (0.1 * test_cw.speed)
        self.assertEqual(test_cw.color_list, new_color)
        # any color not changing is a direction we are not moving
        self.assertEqual(stop, [False, False, True])
        test_cw.base.destroy()

    def test_change_background_two_axis(self):
        config = {'colors': ['g', 'r'],
                  'variance': [0.2, 0.7],
                  'static': 0.1,
                  'win': False}
        loadPrcFileData("", "window-type offscreen")
        test_cw = cw.ColorWorld(config)
        # force some variables to be what we want them to be.
        test_cw.color_list = [0.5, 0.5, 0.5]
        new_color = test_cw.color_list
        # x, y, z; r, g, b
        # {x: r, y: b, z: None} corresponds to {0: 0, 1: 2, 2: None}
        test_cw.color_dict = {0: 0, 1: 2, 2: None}
        move = LVector3(0.1, 0.1, 0)
        stop = test_cw.change_background(move)
        new_color[0] = 0.5 + (0.1 * test_cw.speed)
        new_color[1] = 0.5 + (0.1 * test_cw.speed)
        self.assertEqual(test_cw.color_list, new_color)
        self.assertEqual(stop, [False, False, True])
        test_cw.base.destroy()


if __name__ == "__main__":
    unittest.main(verbosity=2)