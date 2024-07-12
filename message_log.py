# import dependencies
from typing import Iterable, List, Reversible, Tuple
import textwrap
import tcod

import color

# used to save and display messages in the message log
class Message:

    def __init__( self, text: str, fg: Tuple[ int, int, int ] ):

        self.plain_text = text
        self.fg = fg
        self.count = 1

    # the full text of this message, including the count if necessary
    @property
    def full_text( self ) -> str:

        if self.count > 1:

            return f"{ self.plain_text } (x{ self.count })"
        
        return self.plain_text
    
#
class MessageLog:

    def __init__( self ) -> None:

        self.messages: List[ Message ] = []

    # add a message to this log, if "stack" is true, then the message can
    # stack with a previous message of the same text
    def add_message(
        self, text: str, fg: Tuple[ int, int, int ] = color.white, *, stack: bool = True
    ) -> None:
        
        if stack and self.messages and text == self.messages[ -1 ].plain_text:

            self.messages[ -1 ].count += 1

        else:

            self.messages.append( Message( text, fg ) )

    # render this log over the given area
    def render(
        self, console: tcod.console.Console, x: int, y: int, width: int, height: int
    ) -> None:
        
        self.render_messages( console, x, y, width, height, self.messages )

    # return a wrapped text message
    @staticmethod
    def wrap( string: str, width: int ) -> Iterable[ str ]:

        for line in string.splitlines(): # handle newlines in messages

            yield from textwrap.wrap(

                line, width, expand_tabs=True
            )

    # the "messages" are rendered starting at the last message and working backwards
    @classmethod
    def render_messages(
        cls,
        console: tcod.console.Console,
        x: int,
        y: int,
        width: int,
        height: int,
        messages: Reversible[ Message ]
    ) -> None:
        
        y_offset = height - 1

        # step through each message in the log
        for message in reversed( messages ):

            for line in reversed( list( cls.wrap( message.full_text, width ) ) ):

                console.print( x=x, y=y + y_offset, string=line, fg=message.fg )

                y_offset -= 1

                if y_offset < 0:

                    return # no more space to print messages