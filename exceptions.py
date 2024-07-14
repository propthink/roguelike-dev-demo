# exception raised when an action is impossible to be performed,
# the reason is given as the exception message
class Impossible( Exception ):

    pass

# can be raised to exit the game without automatically saving
class QuitWithoutSaving( SystemExit ):

    pass