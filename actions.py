# import dependencies
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from engine import Engine

    from entity import Entity

# interface for all subclasses
class Action:

    # engine is the scope of the action, entity is the object performing the action
    # this method must be overridden by all subclasses
    def perform( self, engine: Engine, entity: Entity ) -> None:

        raise NotImplementedError()

# used to quit application on user request
class EscapeAction( Action ):

    def perform( self, engine: Engine, entity: Entity ) -> None:

        raise SystemExit()
    
#
class ActionWithDirection( Action ):

    def __init__( self, dx: int, dy: int ):

        super().__init__()

        self.dx = dx
        self.dy = dy

    # this method must be overridden by all subclasses
    def perform( self, engine: Engine, entity: Entity ) -> None:

        raise NotImplementedError()
    
# attacks an enemy entity if it exists on the target tile
class MeleeAction( ActionWithDirection ):

    def perform( self, engine: Engine, entity: Entity ) -> None:

        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        target = engine.game_map.get_blocking_entity_at_location( dest_x, dest_y )

        if not target:

            return # no entity to attack
        
        print( f"you kick the {target.name}, it doesn't seem to do much..." )

# move the player in the specified direction
class MovementAction( ActionWithDirection ):

    def perform( self, engine: Engine, entity: Entity ) -> None:

        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        if not engine.game_map.in_bounds( dest_x, dest_y ):

            return # destination is out of bounds
        
        if not engine.game_map.tiles[ "walkable" ][ dest_x, dest_y ]:

            return # destination is blocked by a tile
        
        if engine.game_map.get_blocking_entity_at_location( dest_x, dest_y ):

            return # destination is blocked by an entity
        
        entity.move( self.dx, self.dy )

# decides to attack or move depending on the contents of the target tile
class BumpAction( ActionWithDirection ):

    def perform( self, engine: Engine, entity: Entity ) -> None:

        dest_x = entity.x + self.dx
        dest_y = entity.y + self.dy

        if engine.game_map.get_blocking_entity_at_location( dest_x, dest_y ):

            return MeleeAction( self.dx, self.dy ).perform( engine, entity )
        
        else:

            return MovementAction( self.dx, self.dy ).perform( engine, entity )