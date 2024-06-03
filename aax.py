"""aax
convert a number x to ascii art
we need to provide an image with the number label
and a file with all the digits of that number
additionally provide colors and output size

Usage:
    aax.py [--summary] [--width=W] [--height=H] [--bg=NAME] [--fg=NAME] [--xbg=NAME] [--xfg=NAME] [--image=PATH] [--digits=PATH]

Options:
    -w,--width=W         output width [default: 25]
    -h,--height=H        output height [default: 16]
    --bg=NAME         background color [default: BLACK]
    --fg=NAME         foreground color [default: WHITE]
    --xbg=NAME        number's background color [default: BLACK]
    --xfg=NAME        number's background color [default: RED]
    -i,--image=PATH      the input image white/black [default: ./pi.png]
    -d,--digits=PATH     the input file for the digits [default: ./pi.txt]
    -s,--summary         print the summary, i.e. how many digits we need to print

Valid Color Names:
    WHITE
    BLACK
    BLUE
    CYAN
    GREEN
    MAGENTA
    RED
    YELLOW
"""

import os
from functools import cache

import cv2
import re
import logging

from docopt import docopt
from tabulate import tabulate
from colorama import init, Fore, Back
from colorama.ansi import AnsiBack, AnsiFore
from typing import Union

init(autoreset=True)


def fix_path_fn(path: str) -> str:
    return path.replace("${HOME}", os.environ["HOME"]).replace("~", os.environ["HOME"])


class AAx:
    def __init__(self, image_path: str, digits_path: str, bg: str, fg: str, x_bg: str, x_fg: str):
        self.image_path = image_path
        self.digits_path = digits_path
        self.bg = self.str_to_color(color=bg, src=Back)
        self.fg = self.str_to_color(color=fg, src=Fore)
        self.x_bg = self.str_to_color(color=x_bg, src=Back)
        self.x_fg = self.str_to_color(color=x_fg, src=Fore)

        self.output = ""
        self.freq_x_digits = {}
        self.freq_bg_digits = {}

    @classmethod
    @cache
    def str_to_color(cls, color: str, src: Union[AnsiFore, AnsiBack]) -> str:
        src = {
            "BLACK": src.BLACK,
            "WHITE": src.WHITE,
            "BLUE": src.BLUE,
            "CYAN": src.CYAN,
            "GREEN": src.GREEN,
            "MAGENTA": src.MAGENTA,
            "RED": src.RED,
            "YELLOW": src.YELLOW
        }
        return src[color.strip().upper()]

    def run(self, width: int, height: int) -> str:
        digits = re.sub(r"[.\s]+", "", open(self.digits_path).read())
        if len(digits) < width * height:
            msg = f"""
            the number of digits in '{self.digits_path}' ({len(digits)}) is less than 
            the output size {width}x{height}={width * height}\nSolution: add more
            digits to the file or reduce output size
            """
            logging.error(msg)
            self.output = ""
            self.x_bg = {}
            self.x_fg = {}
            return ""

        image_x = cv2.imread(self.image_path, cv2.COLOR_BGR2GRAY)
        image_a = cv2.cvtColor(image_x, cv2.COLOR_BGR2GRAY)

        image_b = cv2.resize(image_a, (width, height), interpolation=cv2.INTER_AREA)
        image_c = cv2.threshold(image_b, 192, 255, cv2.THRESH_BINARY)[1]

        freq_fg_digits = {str(x): 0 for x in range(10)}
        freq_bg_digits = {str(x): 0 for x in range(10)}

        output = ""
        k, nl = 0, ""
        for i in range(height):
            output += nl
            nl = "\n"
            for j in range(width):
                digit = digits[k]
                k += 1

                if image_c[i, j] != 0:
                    fg_color = self.fg
                    bg_color = self.bg
                    freq_bg_digits[digit] += 1
                else:
                    fg_color = self.x_fg
                    bg_color = self.x_bg
                    freq_fg_digits[digit] += 1

                output += fg_color + bg_color + digit

        self.output = output
        self.freq_x_digits = freq_fg_digits
        self.freq_bg_digits = freq_bg_digits

        return output

    def summary_table(self):
        lines = []

        x_tuple = ("X Digit", self.freq_x_digits, self.x_fg, self.x_bg)
        o_tuple = ("Digit", self.freq_bg_digits, self.fg, self.bg)

        for row_title, freq, fg, bg in (x_tuple, o_tuple):
            line = []
            for x in range(10):
                sx = str(x)
                fx = str(freq[sx])

                text = bg + fg + f"[{sx}]={fx}"

                line.append(text)

            lines.append(line)

        s = sum([x for x in self.freq_x_digits.values()]) + sum([x for x in self.freq_bg_digits.values()])
        table_text = tabulate(lines, tablefmt="simple")
        table_text += f"\nTotal={s} digits"
        return table_text


if __name__ == "__main__":
    args = docopt(__doc__)

    aax = AAx(image_path=fix_path_fn(args["--image"]),
              digits_path=fix_path_fn(args["--digits"]),
              bg=args["--bg"].upper(),
              fg=args["--fg"].upper(),
              x_bg=args["--xbg"].upper(),
              x_fg=args["--xfg"].upper())

    frame = aax.run(width=int(args["--width"]), height=int(args["--height"]))
    print(frame)

    if args["--summary"]:
        table = aax.summary_table()
        print("")
        print("Summary Table w/frequencies")
        print(table)
