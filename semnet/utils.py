
import re


def space_sentencestops(text_str):
    """ Space end of sentence punctuation marks e.g. Bad stop.Good stop. --> Bad stop. Good stop. And remove spaces before end marks e.g. Bad .Good --> Bad. Good."""
    for c in '.;!?,:':
        rx = rf"(\{c}(?=[a-zA-Z]))"
        text_str = re.sub(rx, f"{c} ", text_str)

    rx = r"((?<=[a-zA-Z0-9])\s(?=[.,?!;:]))"
    text_str = re.sub(rx, '', text_str)

    return text_str

def remove_numerical_commas(text_str):
    """ Remove commas from numerical numbers e.g. 1,000,000 --> 1000000 """
    rx = r"((?<=\d)\,(?=\d))"
    return re.sub(rx, "", text_str)

def remove_dashes(text_str):
    """ Remove dashes between acronym-styled words where the character preceding the dash is an upper-case letter and the character following the dash is either an upper-case letter or digit, e.g. COVID-19 --> COVID19. one-to-one --> one-to-one."""
    rx = r"((?<=[A-Z])\-(?=[A-Z|\d]))"
    return re.sub(rx, "", text_str)


def remove_bullets(text_str):
    """ """
    # Remove bullets and replace with full stop
    rx = r"(?<=[^.:?!;])(?: •)"
    text_str = re.sub(rx, '.', text_str)

    # Remove bullets and space
    rx = r"(?: •)"
    text_str = re.sub(rx, '', text_str)
    return text_str


def sub_common_corrections(text_str):
    corrections = {
        "percent": "%",
        "per cent": "%"
    }
    for k, v in corrections.items():
        rx = fr"((?:{k}| {k}))"
        text_str = re.sub(rx, v, text_str)
    return text_str


def replace_MM_abreviations(text_str):
    refs = ['mott macdonald', 'mm', 'mml', 'motts', 'mottmac', 'mmd']
    for ref in refs:
        rx = rf"\b({ref})\b"
        text_str = re.sub(rx, 'Mott MacDonald', text_str, flags=re.IGNORECASE)
    return text_str
