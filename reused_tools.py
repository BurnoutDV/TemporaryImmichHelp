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

import re
import readline
import sys


def recursive_input_regex(prompt: str = "", default_regex: str = "") -> str:
    """
    Recursive annoying input for a str that is supposed to be proper regex..will keep nagging you until
    it is done

    :param prompt: the default input prompt
    :param default_regex: prefilled text
    :return:
    """
    text = input_with_prefill(prompt, default_regex)
    try:
        re.compile(text)
        return text
    except re.error:
        print("Regex seems to be malformed, try again:")
        return recursive_input_regex(prompt, default_regex)


def recursive_number_input(min_value: int, max_value: int) -> int:
    """
    Repeats the input of a number till its actually a number and within the limits assigned
    :param min_value: minimum number that is allowed, its an inclusive minima
    :param max_value: maximum number that is allowed, its an inclusive maxima
    :return:
    """
    written = input("Selection: ")
    try:
        number = int(written)
    except ValueError:
        print("Input was not a natural number, repeat.")
        return recursive_number_input(min_value, max_value) # if you do this 255 times python might not like you anymore#
    if number < min_value or number > max_value:
        print(f"Input was not in the designated limits ({min_value} >= <value> <= {max_value}), repeat")
        return recursive_number_input(min_value, max_value)
    return number

def recursive_minimum_str_input(prompt: str = "", min_length: int = 3) -> str:
    """
    Simple console helper function to make sure that a string contains some text

    :param prompt: the default input prompt
    :param min_length: minimum number of characters
    :return:
    """
    written = input(prompt)
    if len(written) < min_length:
        print(f"The input string has to be at least {min_length} characters long. Retrying.")
        return recursive_minimum_str_input(prompt, min_length)
    return written


def sizeof_fmt(num: int, suffix="B") -> str:
    """
    Human readeable size

    https://stackoverflow.com/a/1094933

    https://web.archive.org/web/20111010015624/http://blogmag.net/blog/read/38/Print_human_readable_file_size
    :param int num: size in bytes
    :param str suffix: suffix after size identifier, like GiB
    """
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"

def input_with_prefill(prompt: str, text: str) -> str:
    """
    A slightly modified input field that allows to prewrite the input text
    :param prompt: normal input(prompt)
    :param text: text you want to pre-write
    :return: the input text
    """
    def hook():
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = input(prompt)
    readline.set_pre_input_hook()
    return result

def simple_progress_bar(current: float,
                        maxi: float,
                        pre: str= "",
                        suf: str= "",
                        out=sys.stdout,
                        clear: bool=False,
                        clear_chr: chr=" ") -> bool | None:
    """
        Simple Progress Bar, any other print called between will break it

        :param float current: current absolute numer
        :param float maxi: upper treshhold
        :param str pre: Additional text before bar
        :param str suf: Additional text after the bar
        :param file out: theoretical output, cant imagine anything else than console making sense
        :param bool clear: if TRUE, does not draw a progress bar but just an empty line
        :param chr clear_chr: character used for the clear line
        :return: False if no shutil is available or parameters got the wrong type
    """
    try:
        import shutil
    except ImportError:
        print("Import Error", file=out)
        return False
    try:
        current = float(current)
        maxi = float(maxi)
        pre = str(pre)
        suf = str(suf)
    except ValueError:
        print("Parameter malformed", file=out)
        return False
    if current > maxi:
        current = maxi  # 100%
    console_length, row = shutil.get_terminal_size()
    del row
    if clear:
        print(clear_chr*console_length)
        return None
    extra_space = console_length - len(pre) - len(suf) - 3  # 3 character long garnish
    extra_length = round((current / maxi) * extra_space)
    if extra_length == extra_space:
        arrow = "="
    else:
        arrow = ">"
    the_bar = "="*extra_length + arrow + " "*(extra_space-extra_length)
    print(pre + "|" + the_bar + "|" + suf, file=out, end="\r")
    return True


if __name__ == "__main__":
    print("This file is part of TemporarImmichHelp, but does nothing in itself. Run main.py")