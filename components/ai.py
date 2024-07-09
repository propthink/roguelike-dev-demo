# import dependencies
from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import numpy as np
import tcod

from actions import Action, MeleeAction, MovementAction, WaitAction # type: ignore

if TYPE_CHECKING:
    from entity import Actor # type: ignore

# basic ai functionality for enemy entities
class BaseAI( Action ):

    # implemented by subclass
    def perform( self ) -> None:

        raise NotImplementedError()
    
    # compute and return a path to the target position,
    # if there is no valid path then returns an empty list
    def get_path_to( self, dest_x: int, dest_y: int ) -> List[ Tuple[ int, int ] ]:

        # copy the walkable array
        cost = np.array( self.entity.gamemap.tiles[ "walkable" ], dtype=np.int8 )

        for entity in self.entity.gamemap.entities:

            # check that an entity blocks movement and the cost isn't zero (blocking)
            if entity.blocks_movement and cost[ entity.x, entity.y ]:

                # add to the cost of a blocked position, a lower number means more enemies
                # will crowd behind each other in hallways, a higher number means enemies 
                # will take longer paths in order to surround the player
                cost[ entity.x, entity.y ] += 10

        # create a graph from the cost array and pass that graph to a new pathfinder
        graph = tcod.path.SimpleGraph( cost=cost, cardinal=2, diagonal=3 )

        pathfinder = tcod.path.Pathfinder( graph )

        pathfinder.add_root( ( self.entity.x, self.entity.y ) ) # start position

        # compute the path to the destination and remove the starting point
        path: List[ List[ int ] ] = pathfinder.path_to( ( dest_x, dest_y ) )[ 1: ].tolist()

        # convert from List[ List[ int ] ] to List[ Tuple[ int, int ] ]
        return [ ( index[ 0 ], index[ 1 ] ) for index in path ]
    
# implementation of base ai for hostile entities
class HostileEnemy( BaseAI ):

    def __init__( self, entity: Actor ):

        super().__init__( entity )
        self.path: List[ Tuple[ int, int ] ] = []

    # perform an action based on the distance from the player entity
    def perform( self ) -> None:

        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max( abs( dx ), abs( dy ) ) # Chebychev distance

        # if the player is right next to the entity, attack the player
        if self.engine.game_map.visible[ self.entity.x, self.entity.y ]:

            if distance <= 1:

                return MeleeAction( self.entity, dx, dy ).perform()
            
            self.path = self.get_path_to( target.x, target.y )

        # if the player can see the entity, but the entity is too far away to attack,
        # then move towards the player
        if self.path:

            dest_x, dest_y = self.path.pop( 0 )

            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y
            ).perform()
        
        # if the entity is not in the player's vision, simply wait
        return WaitAction( self.entity ).perform()
