# configuration for color space

# possible list items: 'r': red, 'g': green, 'b': blue.
# list corresponds to x, y first index is what varies with x,
# second index varies with y, use None if you don't want an
# color to vary with that axis, this means moving in that
# direction will do nothing.

colors = [None, 'g']

# if training, set this to determine which direction to use for first color match
# right, left, front, back or None
# this must match up with the axis. if using x axis, use right or left. if using y axis,
# use front or back. if using x and y axis, can be ['front', 'right']. order irrelevant,
# but number of match directions must match number of colors used.
match_direction = ['right']
# fixed_color = None
# if fixed_color is used, always starts in center, otherwise, start position is random.

# all blue: if static low, dark blue, static high, yellow/white
# all red:  if static low, dark red, static high, teal/white
# all green: if static low, dark green, static high, lavender/white

# I suppose could eventually want to make this different for all
# colors that are varying. Square is designed for a range of 0.5
# c_range = [0.2, 0.7]
c_range = [0.2, 0.7]
# if there is a color that does not vary,
# this is its value
static = 0.1

# how close to a color to get reward
tolerance = 0.01

# resolution = [1024, 768]