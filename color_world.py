from __future__ import division
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import ActorNode, Camera
from panda3d.core import WindowProperties, NodePath, LVector3
from panda3d.core import LineSegs
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
        self.variance = config['variance']
        # adjustment to speed so corresponds to gobananas task
        # 7 seconds to cross original environment
        # speed needs to be adjusted to both speed in original
        # environment and variance of colors
        # self.speed = 0.05 * (self.variance[1] - self.variance[0])
        self.speed = 0.05
        # map avatar variables
        self.render2 = None
        self.render2d = None
        self.last_avt = [0, 0]
        self.map_avt_node = []

        # need a multiplier to the joystick output to tolerable speed
        self.vel_base = 3
        self.max_vel = [500, 500, 0]

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
            print self.base.win.get_size()
            sq_node = square.setup_square(config)
            self.setup_display2(sq_node, config)

        # create the avatar
        self.avatar = NodePath(ActorNode("avatar"))
        self.avatar.reparentTo(self.base.render)
        self.avatar.setH(self.base.camera.getH())
        self.base.camera.reparentTo(self.avatar)
        self.base.camera.setPos(0, 0, 0)
        self.avatar.setPos(-10, -10, 2)
        self.frameTask = self.base.taskMgr.add(self.frame_loop, "frame_loop")
        self.frameTask.last = 0  # task time of the last frame
        self.base.setBackgroundColor(self.color_list[:])
        # print 'end init'

    def frame_loop(self, task):
        dt = task.time - task.last
        task.last = task.time
        self.velocity = self.inputs.poll_inputs(self.velocity)
        move = self.move_avatar(dt)
        stop = self.change_background(move)
        self.move_map_avatar(move, stop)
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
            for key, value in self.color_dict.iteritems():
                if value is not None:
                    stop[key] = False
                    # keys correspond to x,y,z
                    # values correspond to r,g,b
                    if key == 2:
                        # need to work on this. z should
                        # be at min when both x and y are at max
                        # z axis is treated differently
                        z_move = (move[0] + move[1])/2
                        # print z_move
                        self.color_list[value] -= z_move
                    else:
                        self.color_list[value] += move[key]
                    if self.color_list[value] < self.variance[0]:
                        self.color_list[value] = self.variance[0]
                        stop[key] = True
                    elif self.color_list[value] > self.variance[1]:
                        self.color_list[value] = self.variance[1]
                        stop[key] = True
            self.base.setBackgroundColor(self.color_list[:])
            # print self.base.getBackgroundColor()
        return stop

    def move_map_avatar(self, move, stop):
        # print move
        # avatar is mapped assuming variance of 0.5. What do I need to
        # change to use a different variance? variance of one is twice
        # the
        if move:
            avt = LineSegs()
            avt.setThickness(1)
            avt.setColor(1, 1, 1)
            # print 'last', self.last_avt
            avt.move_to(self.last_avt[0], 1, self.last_avt[1])
            new_move = [i + j for i, j in zip(self.last_avt, move)]
            if stop[0]:
                new_move[0] = self.last_avt[0]
            if stop[1]:
                new_move[1] = self.last_avt[1]
            # print 'new', new_move
            self.last_avt = [new_move[0], new_move[1]]
            avt.draw_to(new_move[0], 1, new_move[1])
            self.map_avt_node.append(self.render2d.attach_new_node(avt.create()))
            # can't let too many nodes pile up
            if len(self.map_avt_node) > 299:
                for i, j in enumerate(self.map_avt_node):
                    j.removeNode()
                    if i > 49:
                        break
                del self.map_avt_node[0:50]

    def setup_display2(self, display_node, config):
        props = WindowProperties()
        props.setCursorHidden(True)
        if config.get('resolution'):
            props.setSize(750, 750)
            props.setOrigin(-int(config['resolution'][0]), 0)
        else:
            props.setSize(300, 300)
            props.setOrigin(10, 10)
        window2 = self.base.openWindow(props=props, aspectRatio=1)
        self.render2 = NodePath('render2')
        camera = self.base.camList[-1]
        camera.reparentTo(self.render2)
        camera.setPos(0, -5, 0)
        self.render2.attach_new_node(display_node)
        print 'render2', self.render2
        self.render2d = NodePath('render2d')
        camera2d = self.base.makeCamera(window2)
        camera2d.reparentTo(self.render2d)


if __name__ == "__main__":
    CW = ColorWorld()
    CW.base.run()