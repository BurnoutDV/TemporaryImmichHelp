#!/usr/bin/env python3
# coding: utf-8
# Copyright 2025 by BurnoutDV, <development@burnoutdv.com>
#
# This file is part of TemporaryImmichHelp.
#
# TemporaryImmichHelp is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# TemporaryImmichHelp is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# @license GPL-3.0-only <https://www.gnu.org/licenses/gpl-3.0.en.html>

# Yes yes, i am aware that there are 2000 libraries that doe this already, but I dont feel like importing dependencies.

from typing import Literal

# Colours
colors = {
    'pure_red' : "\033[0;31m",
    'dark_green' : "\033[0;32m",
    'orange' : "\033[0;33m",
    'dark_blue' : "\033[0;34m",
    'bright_purple' : "\033[0;35m",
    'dark_cyan' : "\033[0;36m",
    'dull_white' : "\033[0;37m",
    'pure_black' : "\033[0;30m",
    'bright_red' : "\033[0;91m",
    'light_green' : "\033[0;92m",
    'yellow' : "\033[0;93m",
    'bright_blue' : "\033[0;94m",
    'magenta' : "\033[0;95m",
    'light_cyan' : "\033[0;96m",
    'bright_black' : "\033[0;90m",
    'bright_white' : "\033[0;97m",
    'cyan_back' : "\033[0;46m",
    'purple_back' : "\033[0;45m",
    'white_back' : "\033[0;47m",
    'blue_back' : "\033[0;44m",
    'orange_back' : "\033[0;43m",
    'green_back' : "\033[0;42m",
    'pink_back' : "\033[0;41m",
    'grey_back' : "\033[0;40m",
    'grey' : '\033[38;4;236m',
    'bold' : "\033[1m",
    'underline' : "\033[4m",
    'italic' : "\033[3m",
    'darken' : "\033[2m",
    'invisible' : '\033[08m',
    'reverse_colour' : '\033[07m',
    'reset_colour' : '\033[0m',
    'grey' : "\x1b[90m",
}


def color(text:str, color: Literal['pure_red','dark_green','orange','dark_blue','bright_purple',
                           'dark_cyan','dull_white','pure_black','bright_red','light_green','yellow',
                           'bright_blue','magenta','light_cyan','bright_black','bright_white','cyan_back',
                           'purple_back','white_back','blue_back','orange_back','green_back','pink_back',
                           'grey_back', 'grey','bold','underline','italic','darken','invisible',
                           'reverse_colour','reset_colour','grey']) -> str:
    """
    Simple work function to display colored text in console
    Yes, I know, there are tons of libraries for that.
    This works on my linux machine.

    :param text: Text that get printed
    :param color: one of the preapproved color
    :return: the same text as input but with some op codes
    """
    if color in colors:
        return colors[color] + text + colors['reset_colour']
    else:
        return text


def strike(text : str) -> str:
    """
    Uses some random stuff I found on StackOverload to make strike through characters.
    No clue how far it works
    :param text: Text that is printed striketrough
    :return: a text
    """
    result = ''
    for c in text:
        result = result + c + '\u0336'
    return result


if __name__ == "__main__":
    print("This file is part of TemporarImmichHelp, but does nothing in itself. Run main.py")

