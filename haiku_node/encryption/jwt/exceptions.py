class InvalidJWT(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class InvalidPublicKey(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class JWTSignatureMismatch(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)