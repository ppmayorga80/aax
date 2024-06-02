"""aax
convert a number x to ascii art
we need to provide an image with the number label
and a file with all the digits of that number
additionally provide colors and output size

Usage:
    aax.py [--width=W] [--height=H] [--bg=NAME] [--fg=NAME] [--nbg=NAME] [--nfg=NAME] [--image=PATH] [--digits=PATH]

Options:
    --width=W         output width [default: 25]
    --height=H        output height [default: 16]
    --bg=NAME         background color [default: BLACK]
    --fg=NAME         foreground color [default: WHITE]
    --nbg=NAME        number's background color [default: BLACK]
    --nfg=NAME        number's background color [default: RED]
    --image=PATH      the input image white/black [default: ./pi.png]
    --digits=PATH     the input file for the digits [default: ./pi.txt]


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
import cv2
import re
import logging
from docopt import docopt

from colorama import init, Fore, Back

init(autoreset=True)


def str2bg(name: str) -> str:
    bg_colors = {
        "BLACK": Back.BLACK,
        "WHITE": Back.WHITE,
        "BLUE": Back.BLUE,
        "CYAN": Back.CYAN,
        "GREEN": Back.GREEN,
        "MAGENTA": Back.MAGENTA,
        "RED": Back.RED,
        "YELLOW": Back.YELLOW
    }
    return bg_colors[name.strip().upper()]


def str2fg(name: str) -> str:
    fg_colors = {
        "BLACK": Fore.BLACK,
        "WHITE": Fore.WHITE,
        "BLUE": Fore.BLUE,
        "CYAN": Fore.CYAN,
        "GREEN": Fore.GREEN,
        "MAGENTA": Fore.MAGENTA,
        "RED": Fore.RED,
        "YELLOW": Fore.YELLOW
    }
    return fg_colors[name.strip().upper()]


def fix_path_fn(path: str) -> str:
    return path.replace("${HOME}", os.environ["HOME"]).replace("~", os.environ["HOME"])


def aax(image_path: str, digits_path: str, width: int, height: int, bg: str, fg: str, number_bg: str,
        number_fg: str) -> tuple[str, dict, dict]:
    image_path = fix_path_fn(image_path)
    digits_path = fix_path_fn(digits_path)

    digits = re.sub(r"[.\s]+", "", open(digits_path).read())
    if len(digits) < width * height:
        msg = f"""
        the number of digits in '{digits_path}' ({len(digits)}) is less than 
        the output size {width}x{height}={width * height}\nSolution: add more
        digits to the file or reduce output size
        """
        logging.error(msg)
        return "", {}, {}

    image_x = cv2.imread(image_path, cv2.COLOR_BGR2GRAY)
    image_a = cv2.cvtColor(image_x, cv2.COLOR_BGR2GRAY)

    image_b = cv2.resize(image_a, (width, height), interpolation=cv2.INTER_AREA)
    image_c = cv2.threshold(image_b, 192, 255, cv2.THRESH_BINARY)[1]

    fg_digits = {str(x): 0 for x in range(10)}
    bg_digits = {str(x): 0 for x in range(10)}

    output = ""
    k, nl = 0, ""
    for i in range(height):
        output += nl
        nl = "\n"
        for j in range(width):
            digit = digits[k]
            k += 1

            if image_c[i, j] != 0:
                ascii_char = str2fg(fg) + str2bg(bg)
                bg_digits[digit] += 1
            else:
                ascii_char = str2fg(number_fg) + str2bg(number_bg)
                fg_digits[digit] += 1

            ascii_char += digit
            output += ascii_char

    return output, fg_digits, bg_digits


if __name__ == "__main__":
    args = docopt(__doc__)

    out, fgd, bgd = aax(image_path=args["--image"],
                        digits_path=args["--digits"],
                        width=int(args["--width"]),
                        height=int(args["--height"]),
                        bg=args["--bg"].upper(),
                        fg=args["--fg"].upper(),
                        number_bg=args["--nbg"].upper(),
                        number_fg=args["--nfg"].upper())

    print("")
    for x_digit, freq in fgd.items():
        if freq > 0:
            text = str2bg(args["--nbg"].upper()) + str2fg(args["--nfg"].upper()) + str(x_digit)
            print("XFG:", text, "x", freq)
    for x_digit, freq in bgd.items():
        if freq > 0:
            text = str2bg(args["--bg"].upper()) + str2fg(args["--fg"].upper()) + str(x_digit)
            print("BG:", text, "x", freq)

    print(out)
