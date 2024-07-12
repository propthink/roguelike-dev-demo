# import dependencies
from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

import color  # type: ignore
import exceptions  # type: ignore

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity  # type: ignore

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

# used to quit application on user request
class EscapeAction( Action ):

    def perform( self ) -> None:

        raise SystemExit()
    
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