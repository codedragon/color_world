from __future__ import division
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import ActorNode
from panda3d.core import WindowProperties, NodePath, LVector3
from panda3d.core import LineSegs, OrthographicLens, PNMImage
from panda3d.core import Texture, CardMaker
from inputs import Inputs
import square


class ColorWorld(object):
    def __init__(self, config=None):
        # keep track of velocity, this allows me to counteract joystick with keyboard
        self.velocity = LVector3(0)
        if config is None:
            config = {}
            execfile('config.py', config)

        # self.color_map always corresponds to (r, g, b)
        self.color_dict = square.make_color_map(config['colors'])
        self.color_list = square.set_start_colors(config)

        print 'start color',  self.color_list
        print self.color_dict
        # sets the range of colors for this map
        self.c_range = config['c_range']
        self.color_match = square.set_match_colors(config, self.color_dict)
        # sets the tolerance for how close to a color for reward
        self.color_tolerance = [(i - config['tolerance'], i + config['tolerance']) for i in self.color_match]
        print 'color match', self.color_match
        print 'color tolerance', self.color_tolerance
        map_color_match, factor = square.translate_color_map(config, self.color_dict, self.color_match)
        tolerance = config['tolerance'] * factor
        map_color_tolerance = [(i - tolerance, i + tolerance) for i in map_color_match]

        # adjustment to speed so corresponds to gobananas task
        # 7 seconds to cross original environment
        # speed needs to be adjusted to both speed in original
        # environment and c_range of colors
        # self.speed = 0.05 * (self.c_range[1] - self.c_range[0])
        self.speed = 0.05
        # map avatar variables
        self.render2d = None
        self.last_avt, self.avt_factor = square.translate_color_map(config, self.color_dict, self.color_list)

        # print self.color_list
        # print self.last_avt
        self.map_avt_node = []

        # need a multiplier to the joystick output to tolerable speed
        self.vel_base = 3
        self.max_vel = [500, 500, 0]

        self.card = None

        self.base = ShowBase()
        self.base.disableMouse()
        # assume we are showing windows unless proven otherwise
        if config.get('win', True):
            # only need inputs if we have a window
            self.inputs = Inputs(self.base)
            props = WindowProperties()
            props.setCursorHidden(True)
            props.setForeground(True)
            print config.get('resolution')
            if config.get('resolution'):
                props.set_size(int(config['resolution'][0]), int(config['resolution'][1]))
                props.set_origin(0, 0)
            else:
                props.set_size(600, 600)
                props.set_origin(400, 50)
            self.base.win.requestProperties(props)
            # print self.base.win.get_size()
            sq_node = square.setup_square(config)
            self.setup_display2(sq_node, config)
            self.plot_match_space(map_color_tolerance)

        # create the avatar
        self.avatar = NodePath(ActorNode("avatar"))
        self.avatar.reparentTo(self.base.render)
        self.avatar.setH(self.base.camera.getH())
        self.base.camera.reparentTo(self.avatar)
        self.base.camera.setPos(0, 0, 0)
        self.avatar.setPos(-10, -10, 2)
        self.started_game = self.base.taskMgr.doMethodLater(5, self.start_game, 'start_game')
        self.showed_match = self.base.taskMgr.add(self.show_match_sample, 'match_image')
        self.frameTask = None
        # print 'end init'

    def show_match_sample(self, task):
        print self.color_match[:]
        # match_image.fill(*self.color_match[:])
        card = CardMaker('card')
        color_match = self.color_match[:]
        color_match.append(1)
        print color_match
        card.set_color(*color_match[:])
        size = 10
        card.set_frame(-12, -8, 0, 4)
        #card.set_frame(-1 * size, 0 * size, -0.5 * size, 0.5 * size)
        # self.card = NodePath(card.generate())
        # self.base.camera.reparentTo(self.card)
        self.card = self.base.render.attach_new_node(card.generate())

    def start_game(self, task):
        self.base.taskMgr.remove('match_image')
        self.card.detachNode()
        self.frameTask = self.base.taskMgr.add(self.game_loop, "game_loop")
        self.frameTask.last = 0  # initiate task time of the last frame
        self.base.setBackgroundColor(self.color_list[:])
        return task.done

    def game_loop(self, task):
        dt = task.time - task.last
        task.last = task.time
        self.velocity = self.inputs.poll_inputs(self.velocity)
        move = self.move_avatar(dt)
        stop = self.change_background(move)
        self.move_map_avatar(move, stop)
        match = self.check_color_match()
        if match:
            print 'yay'
            return task.done
        return task.cont

    def move_avatar(self, dt):
        # print 'velocity', self.velocity
        # this makes for smooth (correct speed) diagonal movement
        # print 'velocity', self.velocity
        magnitude = max(abs(self.velocity[0]), abs(self.velocity[1]))
        move = None
        if self.velocity.normalize():
            # go left in increasing amount
            # print 'dt', dt
            # print 'normalized'
            # print 'velocity', self.velocity
            # print 'magnitude', magnitude
            self.velocity *= magnitude
            # print 'velocity', self.velocity
            # this makes for smooth movement
            move = self.velocity * self.vel_base * dt
            # print move
            self.avatar.setFluidPos(self.avatar, move)
        return move

    def change_background(self, move):
        stop = [True, True, True]
        if move:
            # print move
            move *= self.speed
            for i in range(3):
                value = self.color_dict[i]
                if value is not None:
                    stop[i] = False
                    # keys correspond to x,y,z
                    # values correspond to r,g,b
                    if i == 2:
                        # z axis is treated differently
                        # need to work on this. z should
                        # be at min when both x and y are at max
                        # taking the average is not quite right...
                        z_move = (move[0] + move[1])/2
                        # print z_move
                        self.color_list[value] -= z_move
                    else:
                        self.color_list[value] += move[i]
                    if self.color_list[value] < self.c_range[0]:
                        self.color_list[value] = self.c_range[0]
                        stop[i] = True
                    elif self.color_list[value] > self.c_range[1]:
                        self.color_list[value] = self.c_range[1]
                        stop[i] = True
            self.base.setBackgroundColor(self.color_list[:])
            # print self.base.getBackgroundColor()
        return stop

    def move_map_avatar(self, move, stop):
        # print move
        # avatar is mapped assuming c_range of 0.5. What do I need to
        # change to use a different c_range? c_range of one is twice
        # the
        if move:
            avt = LineSegs()
            avt.setThickness(1)
            avt.setColor(1, 1, 1)
            # print 'last', self.last_avt
            avt.move_to(self.last_avt[0], -5, self.last_avt[1])
            new_move = [i + (j * self.avt_factor) for i, j in zip(self.last_avt, move)]
            # new_move = [i + j for i, j in zip(self.last_avt, move)]
            # would it be better to have a local stop condition?
            if stop[0]:
                new_move[0] = self.last_avt[0]
                # print 'stop x', self.last_avt[0]
            if stop[1]:
                new_move[1] = self.last_avt[1]
                # print 'stop y', self.last_avt[1]
            # print 'new', new_move
            self.last_avt = [new_move[0], new_move[1]]
            avt.draw_to(new_move[0], -5, new_move[1])
            self.map_avt_node.append(self.render2d.attach_new_node(avt.create()))
            # can't let too many nodes pile up
            if len(self.map_avt_node) > 299:
                for i, j in enumerate(self.map_avt_node):
                    j.removeNode()
                    if i > 49:
                        break
                del self.map_avt_node[0:50]

    def check_color_match(self):
        # print 'match this', self.color_tolerance
        # print self.color_list
        check_color = [j[0] < self.color_list[i] < j[1] for i, j in enumerate(self.color_tolerance)]
        # print check_color
        if all(check_color):
            return True
        else:
            return False

    def give_reward(self):
        print 'yay'

    def plot_match_space(self, corners):
        match = LineSegs()
        match.setThickness(1)
        match.setColor(0, 0, 0)
        match.move_to(corners[0][0], -5, corners[1][0])
        match.draw_to(corners[0][1], -5, corners[1][0])
        match.draw_to(corners[0][1], -5, corners[1][1])
        match.draw_to(corners[0][0], -5, corners[1][1])
        match.draw_to(corners[0][0], -5, corners[1][0])
        self.render2d.attach_new_node(match.create())

    def setup_display2(self, display_node, config):
        props = WindowProperties()
        props.set_cursor_hidden(True)
        props.set_foreground(False)
        if config.get('resolution'):
            props.setSize(700, 700)
            props.setOrigin(-int(config['resolution'][0] - 5), 5)
        else:
            props.setSize(300, 300)
            props.setOrigin(10, 10)
        window2 = self.base.openWindow(props=props, aspectRatio=1)

        # self.render2 = NodePath('render2')
        # camera = self.base.camList[-1]
        lens = OrthographicLens()
        lens.set_film_size(2, 2)
        lens.setNearFar(-100, 100)
        # camera.node().setLens(lens)
        # self.base.render2d.attach_new_node(camera)

        # camera.reparent_to(self.render2)
        # camera.setPos(0, -5, 0)
        # self.render2.attach_new_node(display_node)
        # print 'render2', self.render2
        self.render2d = NodePath('render2d')
        self.render2d.attach_new_node(display_node)
        camera2d = self.base.makeCamera(window2)
        camera2d.setPos(0, -10, 0)
        camera2d.node().setLens(lens)
        camera2d.reparentTo(self.render2d)


if __name__ == "__main__":
    CW = ColorWorld()
    CW.base.run()
