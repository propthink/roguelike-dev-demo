# import dependencies
from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

import color  # type: ignore
import exceptions  # type: ignore

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item  # type: ignore

# interface for all subclasses
class Action:

    def __init__( self, entity: Actor ) -> None:

        super().__init__()
        self.entity = entity

    # return the engine this action belongs to
    @property
    def engine( self ) -> Engine:

        return self.entity.gamemap.engine

    # perform this action with the objects needed to determine its scope
    def perform( self ) -> None:

        # self.engine is the scope this action is being performed in

        # self.entity is the object performing the action

        # this method must be overridden by Action subclasses
        raise NotImplementedError()
    
# pickup an item and add it to the inventory, if there is room for it
class PickupAction( Action ):

    def __init__( self, entity: Actor ):

        super().__init__( entity )

    def perform( self ) -> None:

        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:

            if actor_location_x == item.x and actor_location_y == item.y:

                if len( inventory.items ) >= inventory.capacity:

                    raise exceptions.Impossible( "Your inventory is full." )
                
                self.engine.game_map.entities.remove( item )

                item.parent = self.entity.inventory

                inventory.items.append( item )

                self.engine.message_log.add_message( f"You picked up the {item.name}!" )

                return
            
        raise exceptions.Impossible( "There is nothing here to pick up." )
    
class ItemAction( Action ):

    def __init__(
            self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__( entity )
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    # return the actor at this action's destination
    @property
    def target_actor( self ) -> Optional[ Actor ]:

        return self.engine.game_map.get_actor_at_location( *self.target_xy )
    
    # invok the item's ability, this action will be given to provide context
    def perform( self ) -> None:

        self.item.consumable.activate( self )
    
#
class DropItem( ItemAction ):

    def perform( self ) -> None:

        self.entity.inventory.drop( self.item )
    
# simply wait
class WaitAction( Action ):

    def perform( self ) -> None:

        pass
    
#
class ActionWithDirection( Action ):

    def __init__( self, entity: Actor, dx: int, dy: int ):

        super().__init__( entity )

        self.dx = dx
        self.dy = dy

    # returns this action's destination
    @property
    def dest_xy( self ) -> Tuple[ int, int ]:

        return self.entity.x + self.dx, self.entity.y + self.dy
    
    # return the blocking entity at this action's destination
    @property
    def blocking_entity( self ) -> Optional[ Entity ]:

        return self.engine.game_map.get_blocking_entity_at_location( *self.dest_xy )
    
    # return the actor at this action's destination
    @property
    def target_actor( self ) -> Optional[ Actor ]:

        return self.engine.game_map.get_actor_at_location( *self.dest_xy )

    # this method must be overridden by all subclasses
    def perform( self ) -> None:

        raise NotImplementedError()
    
# attacks an enemy entity if it exists on the target tile
class MeleeAction( ActionWithDirection ):

    def perform( self ) -> None:

        target = self.target_actor

        if not target:

            raise exceptions.Impossible("Nothing to attack.")
        
        # execute combat sequence
        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize() } attacks { target.name }"

        if self.entity is self.engine.player:

            attack_color = color.player_atk

        else:

            attack_color = color.enemy_atk

        if damage > 0:

            self.engine.message_log.add_message(
                f"{ attack_desc } for { damage } hit points", attack_color
            )
            target.fighter.hp -= damage

        else:

            self.engine.message_log.add_message(
                f"{ attack_desc } but does no damage", attack_color
            )

# move the player in the specified direction
class MovementAction( ActionWithDirection ):

    def perform( self ) -> None:

        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds( dest_x, dest_y ):

            # destination is out of bounds
            raise exceptions.Impossible("That way is blocked.")
        
        if not self.engine.game_map.tiles[ "walkable" ][ dest_x, dest_y ]:

            # destination is blocked by a tile
            raise exceptions.Impossible("That way is blocked.")
        
        if self.engine.game_map.get_blocking_entity_at_location( dest_x, dest_y ):

            # destination is blocked by an entity
            raise exceptions.Impossible("That way is blocked.")
        
        self.entity.move( self.dx, self.dy )

# decides to attack or move depending on the contents of the target tile
class BumpAction( ActionWithDirection ):

    def perform( self ) -> None:

        if self.target_actor:

            return MeleeAction( self.entity, self.dx, self.dy ).perform()
        
        else:

            return MovementAction( self.entity, self.dx, self.dy ).perform()