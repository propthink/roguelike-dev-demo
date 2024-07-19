# import dependencies
from components.ai import HostileEnemy # type: ignore
from components import consumable, equippable # type: ignore
from components.equipment import Equipment # type: ignore
from components.fighter import Fighter # type: ignore
from components.inventory import Inventory # type: ignore
from components.level import Level # type: ignore
from entity import Actor, Item # type: ignore

# human, player
player = Actor(
    char="@",
    color=( 255, 255, 255 ),
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter( hp=30, base_defense=1, base_power=2 ),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200)
)

# monster, orc
orc = Actor(
    char="o",
    color=( 63, 127, 63 ),
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter( hp=10, base_defense=0, base_power=3 ),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35)
)

# monster, troll
troll = Actor(
    char="T",
    color=( 0, 127, 0 ),
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter( hp=16, base_defense=1, base_power=4 ),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100)
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

# fireball scroll
fireball_scroll = Item(
    char="~",
    color=( 255, 0, 0 ),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3)
)

# dagger item
dagger = Item(
    char='/', color=(0, 191, 255), name="Dagger", equippable=equippable.Dagger()
)

# sword item
sword = Item(
    char="/", color=(0, 191, 255), name="Sword", equippable=equippable.Sword()
)

# leather armor item
leather_armor = Item(
    char="[", color=(139, 69, 19), name="Leather Armor", equippable=equippable.LeatherArmor()
)

# chain mail item
chain_mail = Item(
    char="[", color=(139, 69, 19), name="Chain Mail", equippable=equippable.ChainMail()
)