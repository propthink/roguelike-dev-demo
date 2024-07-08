# import dependencies
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine import Engine # type: ignore
    from entity import Entity # type: ignore

#
class BaseComponet:

    entity: Entity # owning entity instance

    # return the engine associated with the entity that owns this componet
    @property
    def engine( self ) -> Engine:

        return self.entity.gamemap.engine