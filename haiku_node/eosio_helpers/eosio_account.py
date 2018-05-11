#Ported from funtions in https://github.com/EOSIO/eos/blob/master/contracts/eosiolib/types.hpp

def string_to_name(s):
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
    if ord(c) >= ord('a') and ord(c) <= ord('z'):
        return (ord(c) - ord('a')) + 6
    if ord(c) >= ord('1') and ord(c) <= ord('5'):
        return (ord(c) - ord('1')) + 1
    return 0
