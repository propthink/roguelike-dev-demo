from enum import auto, Enum

# auto() assigns incrementing integer values automatically
class RenderOrder( Enum ):

    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()