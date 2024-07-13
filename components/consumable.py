from __future__ import annotations
from typing import Optional, TYPE_CHECKING

import actions # type: ignore
import color # type: ignore
import components.inventory # type: ignore
from components.base_component import BaseComponent # type: ignore
from exceptions import Impossible # type: ignore

if TYPE_CHECKING:
    from entity import Actor, Item # type: ignore

class Consumable( BaseComponent ):

    parent: Item

    # try to return the action for this item
    def get_action( self, consumer: Actor ) -> Optional[ actions.Action ]: # type: ignore

        return actions.ItemAction( consumer, self.parent )
    
    # invoke this item's ability, 'action' is the context for this activation
    def activate( self, action: actions.ItemAction ) -> None:

        raise NotImplementedError()
    
    # remove the consumed item from its containing inventory
    def consume( self ) -> None:

        entity = self.parent

        inventory = entity.parent

        if isinstance( inventory, components.inventory.Inventory ):

            inventory.items.remove( entity )
    
class HealingConsumable( Consumable ):

    def __init__( self, amount: int ):

        self.amount = amount

    def activate( self, action: actions.ItemAction ) -> None:

        consumer = action.entity
        amount_recovered = consumer.fighter.heal( self.amount )

        if amount_recovered > 0:

            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                color.health_recovered
            )
            self.consume()
        else:

            raise Impossible( f"Your health is already full." )