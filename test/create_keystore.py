import os
from pathlib import Path

import click

from cryptography.fernet import Fernet

from haiku_node.keystore.keystore import UnificationKeystore


keystore = {
    'app1': {
        'private_key': '-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEApakS8qunhjD+/rLhs90sX4QIh7qWV/6kirBF6plZZHBUHQUz\n90nZQH0zl0feneHXxOEvm1ogLkLtj8qqByzUl7mvzsEdGvtn2AuZt6WzkCThKyhQ\noVU3GVG48xUz8YviR/CruUSlPFeg0DT67IEW3iKYsLWxr9R4D+W5ffRk92/s41Tu\n6b1n4KobTyzvvFSzKlJo6I9a7M4ZvyikWQQri0MUyezMzjDgYNXueGG8gX2VP7OQ\nbvPMb40okN4J3G2gmj9SXf89o8pPDAnk3c1fl1RJ25MjZcVCLFMnI6PBIleCjmtV\n5YqgFznCyLXFcfqieiMb0sPRqhrmB77WjWzVnwIDAQABAoIBAGOdnOBCKnW+Jsgf\n5ysSV6mEKuD7aYa2gFlJkHF3D1MfXOUqiMouJS7rWseglxRXhzlDtC317x4Cbvol\ng0LXSWuHZFmutILSJOq8Zw4Q3T5TfvdFwd6R8JUQGGhMGrUoScS6y3iX98imZPRu\nt2jaY1bmdOzmBVhXKm9c08MS4FgNhKWfruwj8eY5kMOaF/apdsEPN5HmOLDB7xFh\nuRYOg1ZDAVDZeoQTNpOR6eOYuYuONWFMRVA+F4SqWWbmaJjwG55eV+7WDIwJg/5w\nijTCy9A4MMihG3rraQQ5vFJlpVcGV6UnwjOLnEYsMFqedRNaIv5vm/YfLebiWtog\noZw9xvkCgYEA3HF4IKyjAwyWxNeVuQqfevKnry7usrGCyIptyskfRAq6Z88hUV1f\nzCj3ST7Zlh46IrQxaukV7jNmVaKYyAZXptJciqbw3A9GcwvZvKDfZUQmd6jQCtFE\nOeyHkoez+nD+SOfskjWddM3uU3U3PtN0nvMnLQ2b93fvsP189rsgarsCgYEAwGGE\nORDxveTHuYKfLI43s5yVBLHGeRCASwUOqG2Nckbx39MbEzWJQv9HsgS8KzgMHXhn\n7muyv9XaljK+8W7s1UOJfAXTlw+bYZCYw6Org4UWaoK6cVJMOGgAHc2mis1PLZWI\nE8sr+tjioBYRyqp0iY/DRATDbKJnlSAc90KB7G0CgYB8qB3KPFWiL8hCX7bnAL7W\ng8mXIu8QVZkjVkRn2/u2OmrWsSaiIC9AABp2bPgWD9nILiWT02L3ZFGGM4A5/Hws\ndeCm92hUyL6J6DWkmUQ6u6MVH30l4Ni3+K1hiyOXh7YD/EKnG3KCzsDqqOoouOLF\nz7Jjo8KC2mvMpku4KnFWaQKBgQCxhAoXAjyepZFp607nNR/O24hh+YyTP5eyIauB\n3Pzs2uvrRYexNPBAYwCMEnRzSNddBjKYvMYG39VATPkGHP3qV9RwHYw90sfkwiFE\nPS1RQagKhjB1yqPMVKLu3Ul0wLfz7wvOf+ZIJIMRhuvJ33mDSaW7iM2u2zjLUQOJ\nYNQ0DQKBgQDBm7ZvOtdcYmFbTOWQQZp/BpPHvH0/k0FDnsmcbYr3K6wrisF3uCyz\n6hZwSGg4j+ME9UJPc5DBXr97elPhSCipqx10ZcX2Hb5AUS3tizzG+ojeZdDKOCSa\nCTpjvpXSgbCt5ZUcHsMWDpQIPpxhORxwg//D+5ysQBYweGX1/qsojw==\n-----END RSA PRIVATE KEY-----\n', # noqa
        'public_key': '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApakS8qunhjD+/rLhs90s\nX4QIh7qWV/6kirBF6plZZHBUHQUz90nZQH0zl0feneHXxOEvm1ogLkLtj8qqByzU\nl7mvzsEdGvtn2AuZt6WzkCThKyhQoVU3GVG48xUz8YviR/CruUSlPFeg0DT67IEW\n3iKYsLWxr9R4D+W5ffRk92/s41Tu6b1n4KobTyzvvFSzKlJo6I9a7M4ZvyikWQQr\ni0MUyezMzjDgYNXueGG8gX2VP7OQbvPMb40okN4J3G2gmj9SXf89o8pPDAnk3c1f\nl1RJ25MjZcVCLFMnI6PBIleCjmtV5YqgFznCyLXFcfqieiMb0sPRqhrmB77WjWzV\nnwIDAQAB\n-----END PUBLIC KEY-----\n', # noqa
    },
    'app2': {
        'private_key': '-----BEGIN RSA PRIVATE KEY-----\nMIIEogIBAAKCAQEAyC/fG5vnBrGwarNkxgLdYEvYcvmRcC9XnW+h/xLtwlGALlVx\n+1R+MzxcmOTxYzoPAlWKyDlsWp3iNkA0twcRy5S5Sz1NilUwVNNWjaPVAbuab/Bo\n98wVdYHhVc4Jq5honvX/mXp/E+UjWPgWbjrvNtRTM+LfeEi5680rA/q5EfPxUr2Z\n13Z0pr97opGtYCt7Eo0QEIQctQ6t/o2ZDEcvCLKV+gCvWZoSgO98uld3hHXdG2W8\n+DlthJZpZo0kLIDdlVohHNDQfdlTlcTdZwGN+KfNIfhCjr9osB1jQiaprDrL2M0w\njb3V7CcdS6CQ8xtILAeZJ36R0+DMjZP0Mu+UfQIDAQABAoIBADbR/TwXToXjxRcD\nN3aONEd5nbWmqHBbVpfziR5L9bZAEWUe2w7jjYfEYOsxzvTIYnHWMSIxr32FPPx0\nSrtQgUwJ11BGYmSefZTNJye0lNFbqag74tLxHXNHdQjFWpqWKxhU74D9La2qEyr7\nDVF0bCvMq1hLKb1L1TZAwiXd1C6Y7dgnTYK6BVWYSX3sTNDp5FKYupuAGKiTHSIr\nW8Ffjvrcj5yZ6sMa2mZwrVcKorvEV+c6Y3EDQYtmWqKVbVMqf+5xWhgKtQXCMY4t\nVuawkzGNBHXiyPR6dc2mTtsqEUTqICFGdaq86AA+3wTJFev4pZP4iQDC+YKXzZ+9\nK4h3pPUCgYEA8kTFijFzy8XrJYhcGCmsxdIXIwrPVKae7746OkjjJ9zrxPOe4kw6\nb8DhIshvaieXHTRLDyVWgdl+JBTSlNftU8JMmpYW1dPz3rLiiaxFklb7Xr9g2QV6\nl/u67vpj9q/oAhnnu8ytA1PjOJ+rD+zGBmiSfZM43cWD/lqMWf+mMgcCgYEA04iC\nxW5qRizgndkyKcWOFNugSaagBlazyaTz5pryetG/VdY37ijAiieOYDmn5Rp4FJh2\nHgyITmkClrKRUsUx4lWx3sX9u7kn7GL6cl5aN7Xs/authikmiuTaUtLwCfgYdgXz\nxzZ7CaqyR8GCwKRxnt8dOeo6ksipvlu6fG+i1FsCgYASD9qCYQl3CbxsQexLyN+e\np/kdnbKzZvC2gwIoUkLNOAVD273etTwuFL00MKlNysHTZZCrAmeeqq5i1kKU4jxJ\nYFUBuWreajzmP4PwK63MKTv4ZmA8DdKD/jqDkptdSuQLNA84yxujAeAQ2qaQO2DQ\nHX++aPl2X0Fl9y47j3m+hQKBgHQlMChXR+LgITSKXRCyeCDbtla6NoNEd9Lvzzt/\nOERXhkcLKAqMNaulrHcJMTaKIgSs8a3uE6l53wH/aeuYeptbkh5Pd9HrCBCzB/Bj\n/gU4zrc53D0duxvoLDftuf6/Si8DdaacM1JLdzgO+Evt/rTMrK9v/Fk79HegxfQt\nF6qhAoGAChhEwhTr95S2UEw+9JwKVUC3rTC3IH4unLu2k48Q6pK01nGUYP0EVSD6\n1QEHGdNmSUdyGSAYVFT+p9kbgaXtjy0AdUGNGapREZyI+09X7eCBz7A1swRWSD+g\nYbZ54bknWfUyBENKm/a2sI7+4wcB20atHELAXGyUmLBqrUtT0Gs=\n-----END RSA PRIVATE KEY-----\n', # noqa
        'public_key': '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyC/fG5vnBrGwarNkxgLd\nYEvYcvmRcC9XnW+h/xLtwlGALlVx+1R+MzxcmOTxYzoPAlWKyDlsWp3iNkA0twcR\ny5S5Sz1NilUwVNNWjaPVAbuab/Bo98wVdYHhVc4Jq5honvX/mXp/E+UjWPgWbjrv\nNtRTM+LfeEi5680rA/q5EfPxUr2Z13Z0pr97opGtYCt7Eo0QEIQctQ6t/o2ZDEcv\nCLKV+gCvWZoSgO98uld3hHXdG2W8+DlthJZpZo0kLIDdlVohHNDQfdlTlcTdZwGN\n+KfNIfhCjr9osB1jQiaprDrL2M0wjb3V7CcdS6CQ8xtILAeZJ36R0+DMjZP0Mu+U\nfQIDAQAB\n-----END PUBLIC KEY-----\n', # noqa
    },
    'app3': {
        'private_key': '-----BEGIN RSA PRIVATE KEY-----\nMIIEpgIBAAKCAQEA4QwOP1q93KCKLbasK4yvOW5+ZjjO5SAhGr5Qa4C4AawZ5+nd\nKpQZO9ntlYEgA/v4Q4URMOZMYVYSngrJoN7PWUuHDuVzqaaU6wotCtW9q0DarM/z\ngQxtDYkatre5jmyah2cACisDuJ5LVWbx1V/S/+/6v+Z2GYQUsBi/cpv322a82wDj\nHd8G1WYmOpprypM4BPpsjd0W/sgLFqPT0zqYCeoXMfchzW6SBSGeR2tJ3xC3+227\nyJ2dzAOf3Te7a3YcPQEKvHYw5Nc+nuizO4SpcWpBhpEZM3XoRGhCVZs5RuZAzj42\nY01OLu0ASgPcOkmuZGvAz+ZejRF8rR1fOLDP4wIDAQABAoIBAQCN2qmIacxPq6ot\n0n2IHe+9hdaK3LgdWTlEwD205bgW5cKWmqVcV2nofh/yIyhpGoSNGu2RIzl2CWlG\n0Ynyqz+MC72gOCXGBEjONuXZdI1Py1uLnrDg4VJEO+3oyrpd+jsVqmkt/5si3jSi\nKne5heNcjIpEOCKtRsI7lf3nYkTDuDotloJ1/2r57YlGFeqQG8A8l7W4u2IdQzdj\noOLvK9GAzI1l7Da8AxsIoOnFp8A2p8BvdoF2kwEt29Y5B6BURszkbKYViJhQfvgk\ng9IjP/vXOYlql+D2EZsr2dMGmlutB4xr9Eho9fZGRvFqMzFjWS1k5uhi5FPjegk3\nSOONVtTBAoGBAPEwk3zCACM5YhNOUeUpGCHeoKXip0/L3J5LwMF+/id1W0mNKwRz\nr0dHpHYBTUltPiy2Ua4Yd1LnFXIKzVOAzSsE6DxoqXt/UP+W1cU16DMNAK6YWTkY\nSFw5QyhjylZPcRuZFxDIdk8oKHJnLVTCLdaGZklhMvJ44L/0P2NaNKxRAoGBAO7d\nuORXeLTGtdwYBu6t1fU3cUX3PbFU67foa6BQv6oMQneDpUFN78iXaiFBXF6f9BaM\nGNzJZLkfOdUAIEGLjZTNGf4eKouSeEYsecJwCdu+X2HMryivsVzpg3oYZxBoPHui\nfT8UUw2svfANeEyn5ZohvaWtEELxr4lwiNf5cI/zAoGBALokJj+LrfWBbOq/cD7u\n9zv0iIFeKohQKoVUq3/qVZX4YaqjM4btDWJyrT+Rg6dekzSIxQMayMSHqappIcwH\nRNClqeItWFgCi22maHcaQolbyKH23C1PS1E5tFXwphD0oLOO9Bk0zPIMaSLZ9EdM\n0XmWIk0RofM2TSZ4B4/S54HxAoGBAL9yqFEjppRFu9bmzw+X9qeuwzQPoLuz06W4\nPCLm9WdmohNGSTpZK/l7Gk4DI/SXgTxdF0RGilsxotmMW04NevGrncymAvWQ9KNR\n3FkyEUS1hZ9OPYl/n8lXQ9ClJF3rHab+KiJXuOV58VYohaXy37y0lFropeLx8P5Y\nWuW3gDdvAoGBAO9QcfoTMNK1adzu4Zyelp7Hy3QFOBkGhp42SbA1EDao1CycrgG9\nKtb1J4c8UD2XxsFPAdqcagrEk3VlDC7fZf2HDbRq4Tc/aH32jGYOJap5hyp6Cwrg\nWdy0Lvb3CTr24H9YXqYXfJ6hcMMjeG2UbpYccD1ObzRjsJ1ibH0yl3J1\n-----END RSA PRIVATE KEY-----\n', # noqa
        'public_key': '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4QwOP1q93KCKLbasK4yv\nOW5+ZjjO5SAhGr5Qa4C4AawZ5+ndKpQZO9ntlYEgA/v4Q4URMOZMYVYSngrJoN7P\nWUuHDuVzqaaU6wotCtW9q0DarM/zgQxtDYkatre5jmyah2cACisDuJ5LVWbx1V/S\n/+/6v+Z2GYQUsBi/cpv322a82wDjHd8G1WYmOpprypM4BPpsjd0W/sgLFqPT0zqY\nCeoXMfchzW6SBSGeR2tJ3xC3+227yJ2dzAOf3Te7a3YcPQEKvHYw5Nc+nuizO4Sp\ncWpBhpEZM3XoRGhCVZs5RuZAzj42Y01OLu0ASgPcOkmuZGvAz+ZejRF8rR1fOLDP\n4wIDAQAB\n-----END PUBLIC KEY-----\n' # noqa
    }
}


def generate_keystore(app_name):
    password = Fernet.generate_key()
    click.echo(password)

    current_path = Path(os.path.dirname(os.path.abspath(__file__)))
    ks_path = current_path / Path(f'data/keys')
    ks = UnificationKeystore(password, app_name=app_name, keystore_path=ks_path)
    pub = keystore[app_name]['public_key']
    priv = keystore[app_name]['private_key']

    ks.set_rpc_auth_keys(pub, priv)


@click.command()
@click.argument('app_name')
def cli(app_name):
    generate_keystore(app_name)


if __name__ == "__main__":
    cli()
