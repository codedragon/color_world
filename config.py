# configuration for color space

# possible list items: 'r': red, 'g': green, 'b': blue.
# list corresponds to x, y first index is what varies with x,
# second index varies with y, use None if you don't want an
# color to vary with that axis, this means moving in that
# direction will do nothing.

colors = [None, 'g']
# all blue: if static low, dark blue, static high, yellow/white
# all red:  if static low, dark red, static high, teal/white
# all green: if static low, dark green, static high, lavender/white
# I suppose could eventually want to make this different for all
# colors that are varying. Square is designed for a variance of 0.5
# variance = [0.2, 0.7]
variance = [0.2, 0.7]
# if there is a color that does not vary,
# this is its value
static = 0.1

# resolution = [1024, 768]