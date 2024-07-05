# interface for all subclasses
class Action:

    pass

# used to quit application on user request
class EscapeAction( Action ):

    pass

# move the player in the specified direction
class MovementAction( Action ):

    def __init__( self, dx: int, dy: int ):

        super().__init__()

        self.dx = dx

        self.dy = dy