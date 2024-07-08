# import dependencies
from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:

    from engine import Engine

    from entity import Entity

# interface for all subclasses
class Action:

    def __init__( self, entity: Entity ) -> None:

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
    
#
class ActionWithDirection( Action ):

    def __init__( self, entity: Entity, dx: int, dy: int ):

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

    # this method must be overridden by all subclasses
    def perform( self ) -> None:

        raise NotImplementedError()
    
# attacks an enemy entity if it exists on the target tile
class MeleeAction( ActionWithDirection ):

    def perform( self ) -> None:

        target = self.blocking_entity

        if not target:

            return # no entity to attack
        
        print( f"you aggressively tickle the monster" ) # test print

# move the player in the specified direction
class MovementAction( ActionWithDirection ):

    def perform( self ) -> None:

        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds( dest_x, dest_y ):

            return # destination is out of bounds
        
        if not self.engine.game_map.tiles[ "walkable" ][ dest_x, dest_y ]:

            return # destination is blocked by a tile
        
        if self.engine.game_map.get_blocking_entity_at_location( dest_x, dest_y ):

            return # destination is blocked by an entity
        
        self.entity.move( self.dx, self.dy )

# decides to attack or move depending on the contents of the target tile
class BumpAction( ActionWithDirection ):

    def perform( self ) -> None:

        if self.blocking_entity:

            return MeleeAction( self.entity, self.dx, self.dy ).perform()
        
        else:

            return MovementAction( self.entity, self.dx, self.dy ).perform()