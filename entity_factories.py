# import dependencies
from components.ai import HostileEnemy # type: ignore
from components import consumable # type: ignore
from components.fighter import Fighter # type: ignore
from components.inventory import Inventory # type: ignore
from entity import Actor, Item # type: ignore

# human, player
player = Actor(
    char="@",
    color=( 255, 255, 255 ),
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter( hp=30, defense=2, power=5 ),
    inventory=Inventory(capacity=26)
)

# monster, orc
orc = Actor(
    char="o",
    color=( 63, 127, 63 ),
    name="Orc",
    ai_cls=HostileEnemy,
    fighter=Fighter( hp=10, defense=0, power=3 ),
    inventory=Inventory(capacity=0)
)

# monster, troll
troll = Actor(
    char="T",
    color=( 0, 127, 0 ),
    name="Troll",
    ai_cls=HostileEnemy,
    fighter=Fighter( hp=16, defense=1, power=4 ),
    inventory=Inventory(capacity=0)
)

# health potion
health_potion = Item(
    char="!",
    color=(127, 0, 255),
    name="Health Potion",
    consumable=consumable.HealingConsumable(amount=4)
)

# lightning scroll
lightning_scroll = Item(
    char="~",
    color=( 255, 255, 0 ),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5)
)

# confusion scroll
confusion_scroll = Item(
    char="~",
    color=( 207, 63, 255 ),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=10)
)