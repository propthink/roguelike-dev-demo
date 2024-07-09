# import dependencies
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine # type: ignore
    from entity import Entity # type: ignore
    from game_map import GameMap # type: ignore

#
class BaseComponent:

    parent: Entity # owning entity instance

    #
    @property
    def gamemap( self ) -> GameMap:

        return self.parent.gamemap

    # return the engine associated with the entity that owns this componet
    @property
    def engine( self ) -> Engine:

        return self.gamemap.engine