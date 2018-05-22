# Ported from funtions in https://github.com/EOSIO/eos/blob/master/contracts/eosiolib/types.hpp


def string_to_name(s):
    """
    Converts EOS readable base32 string account name to uint64
    :param s: account name as string
    """
    lgth = len(s)
    value = 0
    for i in range(0, 13):
        c = 0
        if i < lgth and i <= 12:
            c = char_to_symbol(s[i])

        if i < 12:
            c &= 0x1f
            c <<= 64 - 5 * (i + 1)

        else:
            c &= 0x0f

        value |= c
    return int(value)


def char_to_symbol(c):
    """
    Converts char to int. Used by string_to_name
    :param c: char value
    """
    if ord(c) >= ord('a') and ord(c) <= ord('z'):
        return (ord(c) - ord('a')) + 6
    if ord(c) >= ord('1') and ord(c) <= ord('5'):
        return (ord(c) - ord('1')) + 1
    return 0


def name_to_string(n):
    """
    Converts EOS uint64 account name to readable base32 string
    :param n: account name as string
    """
    # make sure it's an int
    n = int(n)

    charmap = ".12345abcdefghijklmnopqrstuvwxyz"
    tmp = n
    n_str = ""

    for i in range(0, 13):
        if i == 0:
            t = 0x0f
            t2 = 4
        else:
            t = 0x1f
            t2 = 5
        c = charmap[tmp & t]
        n_str = c + n_str
        tmp >>= t2

    while n_str.endswith("."):
        n_str = n_str.rstrip(".")

    return n_str
