# import dependencies
from __future__ import annotations

import random
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np
import tcod

from actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction # type: ignore

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
    
# a confused enemy will stumble around aimlessly for a given number of turns, then revert back
# to its previous AI. If an actor occupies a tile it is randomly moving into, it will attack
class ConfusedEnemy( BaseAI ):

    def __init__(
            self, entity: Actor, previous_ai: Optional[ BaseAI ], turns_remaining: int
    ):
        super().__init__( entity )
        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform( self ) -> None:

        # revert the AI back to the original state if the effect has run its course
        if self.turns_remaining <= 0:

            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused."
            )
            self.entity.ai = self.previous_ai

        else:

            # pick a random direction
            direction_x, direction_y = random.choice(
                [
                    (-1, -1), # northwest
                    ( 0, -1), # north
                    ( 1, -1), # northeast
                    (-1,  0), # west
                    ( 1,  0), # east
                    (-1,  1), # southwest
                    ( 0,  1), # south
                    ( 1,  1)  # southeast
                ]
            )
            self.turns_remaining -= 1

            # the actor will either try to move or attack in the chosen random direction.
            # it is possible the actor will just bump into the wall, wasting a turn
            return BumpAction( self.entity, direction_x, direction_y ).perform()
    
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
