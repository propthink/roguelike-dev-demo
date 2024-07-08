# import dependencies
from __future__ import annotations

import copy
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING

from render_order import RenderOrder # type: ignore

if TYPE_CHECKING:
    from componets.ai import BaseAI # type: ignore
    from componets.fighter import Fighter # type: ignore
    from game_map import GameMap

#
T = TypeVar( "T", bound="Entity" )

# generic object to represent player, enemy, item, etc.
class Entity:

    #
    gamemap: GameMap

    # initialize object with location, glyph, and color
    def __init__(
        self,
        gamemap: Optional[ GameMap ] = None,
        x: int=0,
        y: int=0,
        char: str="?",
        color: Tuple[ int, int, int ] = ( 255, 255, 255 ),
        name: str="<unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        
        # if gamemap is not provided now then it will be set later
        if gamemap:

            self.gamemap = gamemap
            gamemap.entities.add( self )

    # spawn a copy of this instance at the given location
    def spawn( self: T, gamemap: GameMap, x: int, y: int ) -> T:

        clone = copy.deepcopy( self )
        clone.x = x
        clone.y = y
        clone.gamemap = gamemap
        gamemap.entities.add( clone )
        return clone
    
    # place this entity at a new location, handles moving across GameMaps
    def place( self, x: int, y: int, gamemap: Optional[ GameMap ] = None ) -> None:

        self.x = x
        self.y = y

        if gamemap:

            if hasattr( self, "gamemap" ): # possibly uninitialized

                self.gamemap.entities.remove( self )

            self.gamemap = gamemap

            gamemap.entities.add( self )

    # move the entity by the given amount
    def move( self, dx: int, dy:int ) -> None:

        self.x += dx
        self.y += dy

# an entity capable of performing actions
class Actor( Entity ):

    def __init__(
            
        self,
        *,
        x: int=0,
        y: int=0,
        char: str="?",
        color: Tuple[ int, int, int ] = ( 255, 255, 255 ),
        name: str = "<Unnamed>",
        ai_cls: Type[ BaseAI ],
        fighter: Fighter
    ):
        super().__init__(

            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR
        )
        self.ai: Optional[ BaseAI ] = ai_cls( self )        
        self.fighter = fighter
        self.fighter.entity = self

    # returns true as long as this actor can perform actions
    @property
    def is_alive( self ) -> bool:

        return bool( self.ai )
