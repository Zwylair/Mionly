import sys
from dataclasses import dataclass
import dearpygui.dearpygui as dpg


@dataclass
class FontPreset:
    path: str
    id: str
    size: int
    bind_font_as_default: bool


class CyrillicSupport:
    # Parameters for Cyrillic conversion
    big_let_start = 0x00C0  # Capital "А" in Cyrillic.
    big_let_end = 0x00DF  # Capital "Я" in Cyrillic.
    small_let_end = 0x00FF  # Little "я" in Cyrillic
    remap_big_let = 0x0410  # Initial number for the reassigned Cyrillic alphabet

    alph_len = big_let_end - big_let_start + 1  # adds a shift from large letters to small ones
    alph_shift = remap_big_let - big_let_start  # adds a transition from reassignment to non-reassignment

    def __init__(self, font_preset: FontPreset):
        self.font_preset = font_preset
        self.registry_font()

    def registry_font(self):
        with dpg.font(file=self.font_preset.path, size=self.font_preset.size, id=self.font_preset.id,
                      default_font=self.font_preset.bind_font_as_default):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range(0x0391, 0x03C9)  # Greek character range
            dpg.add_font_range(0x2070, 0x209F)  # Range of upper and lower numerical indices

            # Fixing keyboard input on Windows
            if sys.platform == 'win32':
                biglet = self.remap_big_let  # Initial number for the reassigned Cyrillic alphabet
                for i1 in range(self.big_let_start, self.big_let_end + 1):  # Cyclic switching of large letters
                    dpg.add_char_remap(i1, biglet)  # Reassigning the big letter
                    dpg.add_char_remap(i1 + self.alph_len, biglet + self.alph_len)  # Reassign a small letter
                    biglet += 1  # choose the next letter

                # The letters "Ёё" must be added separately, since they are located elsewhere in the table
                dpg.add_char_remap(0x00A8, 0x0401)
                dpg.add_char_remap(0x00B8, 0x0451)

            # Set font
            if self.font_preset.bind_font_as_default:
                dpg.bind_font(self.font_preset.id)


def decode_string(instr: str):
    if sys.platform == 'win32':
        outstr = []
        for i in range(0, len(instr)):
            char_byte = ord(instr[i])
            if char_byte in range(CyrillicSupport.big_let_start, CyrillicSupport.small_let_end + 1):
                char = chr(ord(instr[i]) + CyrillicSupport.alph_shift)
                outstr.append(char)
            # Checking for "Ё"
            elif char_byte == 0x00A8:
                char = chr(0x0401)
                outstr.append(char)
            # Checking for "ё"
            elif char_byte == 0x00B8:
                char = chr(0x0451)
                outstr.append(char)
            else:
                outstr.append(instr[i])

        return ''.join(outstr)

    else:
        return instr
