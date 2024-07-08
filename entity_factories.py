# import dependencies
from components.ai import HostileEnemy # type: ignore
from components.fighter import Fighter # type: ignore
from entity import Actor # type: ignore

# human, player
player = Actor(
    char="@",
    color=( 255, 255, 255 ),
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter( hp=30, defense=2, power=5 )
)

# monster, orc
orc = Actor(
    char="o",
    color=( 63, 127, 63 ),
    name="Orc",
    ai_cls=HostileEnemy,
    fighter=Fighter( hp=10, defense=0, power=3 )
)

# monster, troll
troll = Actor(
    char="T",
    color=( 0, 127, 0 ),
    name="Troll",
    ai_cls=HostileEnemy,
    fighter=Fighter( hp=16, defense=1, power=4 )
)