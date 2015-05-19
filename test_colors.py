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
                  'c_range': [0.2, 0.7],
                  'static': 0.1}
        # green on x axis, red on y axis, blue static
        color_vertices = square.make_color_vertices(config)
        known = [(0.2, 0.2, 0.1, 1),
                 (0.2, 0.7, 0.1, 1),
                 (0.7, 0.7, 0.1, 1),
                 (0.7, 0.2, 0.1, 1)]
        self.assertEqual(color_vertices, known)

    def test_starting_colors(self):
        # not setting fixed_color, so should return random
        config = {'colors': ['b', 'r'],
                  'c_range': [0.2, 0.7],
                  'static': 0.1}
        color_list = square.set_start_position_colors(config)
        # red and blue between c_range, green static
        # print color_list
        self.assertTrue(0.2 <= color_list[0] <= 0.7)
        self.assertEqual(0.1, color_list[1])
        self.assertTrue(0.2 <= color_list[0] <= 0.7)

    def test_fixed_start_colors(self):
        config = {'colors': ['b', 'r'],
                  'c_range': [0.2, 0.7],
                  'static': 0.1,
                  'match_direction': ['right']}
        color_list = square.set_start_position_colors(config)
        mid = config['c_range'][0] + (config['c_range'][1] - config['c_range'][0])/2
        self.assertEqual([mid, 0.1, mid], color_list)

    def test_fixed_match_single_color(self):
        config = {'colors': ['b'],
                  'c_range': [0.2, 0.7],
                  'static': 0.1,
                  'match_direction': ['left']}
        color_dict = square.make_color_map(config['colors'])
        color_list = square.set_match_colors(config, color_dict)
        self.assertEqual([0.1, 0.1, 0.2], color_list)

    def test_fixed_match_colors(self):
        config = {'colors': ['b'],
                  'c_range': [0.2, 0.7],
                  'static': 0.1,
                  'match_direction': ['right']}
        color_dict = square.make_color_map(config['colors'])
        color_list = square.set_match_colors(config, color_dict)
        self.assertEqual([0.1, 0.1, 0.7], color_list)

    def test_mis_matched_config(self):
        config = {'colors': [None, 'r'],
                  'c_range': [0.2, 0.7],
                  'static': 0.1,
                  'match_direction': ['right']}
        color_dict = square.make_color_map(config['colors'])
        self.assertRaises(NotImplementedError, square.set_match_colors, config, color_dict)

    def test_translate_color_map(self):
        config = {'colors': ['r', 'b'],
                  'c_range': [0.2, 0.7],
                  'static': 0.1}
        color_dict = square.make_color_map(config['colors'])
        # start at extreme ends, should translate to -1, 1
        color_list = (0.2, 0.1, 0.7)
        # after translating,
        x_y = [-1, 1]
        translated, factor = square.translate_color_map(config, color_dict, color_list)
        self.assertAlmostEqual(4, factor)
        self.assertEqual(x_y, translated)

    def test_translate_color_map_expanded(self):
        config = {'colors': ['r', 'b'],
                  'c_range': [0.1, 0.9],
                  'static': 0.1}
        color_dict = square.make_color_map(config['colors'])
        # start at extreme ends, should translate to -1, 1
        color_list = (0.1, 0.1, 0.9)
        # after translating,
        x_y = [-1, 1]
        translated, factor = square.translate_color_map(config, color_dict, color_list)
        self.assertAlmostEqual(2.5, factor)
        self.assertEqual(x_y, translated)

    def test_change_background(self):
        config = {'colors': ['g', 'r'],
                  'c_range': [0.2, 0.7],
                  'static': 0.1,
                  'win': False,
                  'tolerance': 0.1}
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
                  'c_range': [0.2, 0.7],
                  'static': 0.1,
                  'win': False,
                  'tolerance': 0.1}
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