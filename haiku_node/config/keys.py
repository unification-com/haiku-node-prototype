from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

# TODO: These keys will eventually be obtained from different places
keystore = {
    'app1': {
        'private_key': b'-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEApakS8qunhjD+/rLhs90sX4QIh7qWV/6kirBF6plZZHBUHQUz\n90nZQH0zl0feneHXxOEvm1ogLkLtj8qqByzUl7mvzsEdGvtn2AuZt6WzkCThKyhQ\noVU3GVG48xUz8YviR/CruUSlPFeg0DT67IEW3iKYsLWxr9R4D+W5ffRk92/s41Tu\n6b1n4KobTyzvvFSzKlJo6I9a7M4ZvyikWQQri0MUyezMzjDgYNXueGG8gX2VP7OQ\nbvPMb40okN4J3G2gmj9SXf89o8pPDAnk3c1fl1RJ25MjZcVCLFMnI6PBIleCjmtV\n5YqgFznCyLXFcfqieiMb0sPRqhrmB77WjWzVnwIDAQABAoIBAGOdnOBCKnW+Jsgf\n5ysSV6mEKuD7aYa2gFlJkHF3D1MfXOUqiMouJS7rWseglxRXhzlDtC317x4Cbvol\ng0LXSWuHZFmutILSJOq8Zw4Q3T5TfvdFwd6R8JUQGGhMGrUoScS6y3iX98imZPRu\nt2jaY1bmdOzmBVhXKm9c08MS4FgNhKWfruwj8eY5kMOaF/apdsEPN5HmOLDB7xFh\nuRYOg1ZDAVDZeoQTNpOR6eOYuYuONWFMRVA+F4SqWWbmaJjwG55eV+7WDIwJg/5w\nijTCy9A4MMihG3rraQQ5vFJlpVcGV6UnwjOLnEYsMFqedRNaIv5vm/YfLebiWtog\noZw9xvkCgYEA3HF4IKyjAwyWxNeVuQqfevKnry7usrGCyIptyskfRAq6Z88hUV1f\nzCj3ST7Zlh46IrQxaukV7jNmVaKYyAZXptJciqbw3A9GcwvZvKDfZUQmd6jQCtFE\nOeyHkoez+nD+SOfskjWddM3uU3U3PtN0nvMnLQ2b93fvsP189rsgarsCgYEAwGGE\nORDxveTHuYKfLI43s5yVBLHGeRCASwUOqG2Nckbx39MbEzWJQv9HsgS8KzgMHXhn\n7muyv9XaljK+8W7s1UOJfAXTlw+bYZCYw6Org4UWaoK6cVJMOGgAHc2mis1PLZWI\nE8sr+tjioBYRyqp0iY/DRATDbKJnlSAc90KB7G0CgYB8qB3KPFWiL8hCX7bnAL7W\ng8mXIu8QVZkjVkRn2/u2OmrWsSaiIC9AABp2bPgWD9nILiWT02L3ZFGGM4A5/Hws\ndeCm92hUyL6J6DWkmUQ6u6MVH30l4Ni3+K1hiyOXh7YD/EKnG3KCzsDqqOoouOLF\nz7Jjo8KC2mvMpku4KnFWaQKBgQCxhAoXAjyepZFp607nNR/O24hh+YyTP5eyIauB\n3Pzs2uvrRYexNPBAYwCMEnRzSNddBjKYvMYG39VATPkGHP3qV9RwHYw90sfkwiFE\nPS1RQagKhjB1yqPMVKLu3Ul0wLfz7wvOf+ZIJIMRhuvJ33mDSaW7iM2u2zjLUQOJ\nYNQ0DQKBgQDBm7ZvOtdcYmFbTOWQQZp/BpPHvH0/k0FDnsmcbYr3K6wrisF3uCyz\n6hZwSGg4j+ME9UJPc5DBXr97elPhSCipqx10ZcX2Hb5AUS3tizzG+ojeZdDKOCSa\nCTpjvpXSgbCt5ZUcHsMWDpQIPpxhORxwg//D+5ysQBYweGX1/qsojw==\n-----END RSA PRIVATE KEY-----\n', # noqa
        'public_key': b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApakS8qunhjD+/rLhs90s\nX4QIh7qWV/6kirBF6plZZHBUHQUz90nZQH0zl0feneHXxOEvm1ogLkLtj8qqByzU\nl7mvzsEdGvtn2AuZt6WzkCThKyhQoVU3GVG48xUz8YviR/CruUSlPFeg0DT67IEW\n3iKYsLWxr9R4D+W5ffRk92/s41Tu6b1n4KobTyzvvFSzKlJo6I9a7M4ZvyikWQQr\ni0MUyezMzjDgYNXueGG8gX2VP7OQbvPMb40okN4J3G2gmj9SXf89o8pPDAnk3c1f\nl1RJ25MjZcVCLFMnI6PBIleCjmtV5YqgFznCyLXFcfqieiMb0sPRqhrmB77WjWzV\nnwIDAQAB\n-----END PUBLIC KEY-----\n', # noqa
    },
    'app2': {
        'private_key': b'-----BEGIN RSA PRIVATE KEY-----\nMIIEogIBAAKCAQEAyC/fG5vnBrGwarNkxgLdYEvYcvmRcC9XnW+h/xLtwlGALlVx\n+1R+MzxcmOTxYzoPAlWKyDlsWp3iNkA0twcRy5S5Sz1NilUwVNNWjaPVAbuab/Bo\n98wVdYHhVc4Jq5honvX/mXp/E+UjWPgWbjrvNtRTM+LfeEi5680rA/q5EfPxUr2Z\n13Z0pr97opGtYCt7Eo0QEIQctQ6t/o2ZDEcvCLKV+gCvWZoSgO98uld3hHXdG2W8\n+DlthJZpZo0kLIDdlVohHNDQfdlTlcTdZwGN+KfNIfhCjr9osB1jQiaprDrL2M0w\njb3V7CcdS6CQ8xtILAeZJ36R0+DMjZP0Mu+UfQIDAQABAoIBADbR/TwXToXjxRcD\nN3aONEd5nbWmqHBbVpfziR5L9bZAEWUe2w7jjYfEYOsxzvTIYnHWMSIxr32FPPx0\nSrtQgUwJ11BGYmSefZTNJye0lNFbqag74tLxHXNHdQjFWpqWKxhU74D9La2qEyr7\nDVF0bCvMq1hLKb1L1TZAwiXd1C6Y7dgnTYK6BVWYSX3sTNDp5FKYupuAGKiTHSIr\nW8Ffjvrcj5yZ6sMa2mZwrVcKorvEV+c6Y3EDQYtmWqKVbVMqf+5xWhgKtQXCMY4t\nVuawkzGNBHXiyPR6dc2mTtsqEUTqICFGdaq86AA+3wTJFev4pZP4iQDC+YKXzZ+9\nK4h3pPUCgYEA8kTFijFzy8XrJYhcGCmsxdIXIwrPVKae7746OkjjJ9zrxPOe4kw6\nb8DhIshvaieXHTRLDyVWgdl+JBTSlNftU8JMmpYW1dPz3rLiiaxFklb7Xr9g2QV6\nl/u67vpj9q/oAhnnu8ytA1PjOJ+rD+zGBmiSfZM43cWD/lqMWf+mMgcCgYEA04iC\nxW5qRizgndkyKcWOFNugSaagBlazyaTz5pryetG/VdY37ijAiieOYDmn5Rp4FJh2\nHgyITmkClrKRUsUx4lWx3sX9u7kn7GL6cl5aN7Xs/authikmiuTaUtLwCfgYdgXz\nxzZ7CaqyR8GCwKRxnt8dOeo6ksipvlu6fG+i1FsCgYASD9qCYQl3CbxsQexLyN+e\np/kdnbKzZvC2gwIoUkLNOAVD273etTwuFL00MKlNysHTZZCrAmeeqq5i1kKU4jxJ\nYFUBuWreajzmP4PwK63MKTv4ZmA8DdKD/jqDkptdSuQLNA84yxujAeAQ2qaQO2DQ\nHX++aPl2X0Fl9y47j3m+hQKBgHQlMChXR+LgITSKXRCyeCDbtla6NoNEd9Lvzzt/\nOERXhkcLKAqMNaulrHcJMTaKIgSs8a3uE6l53wH/aeuYeptbkh5Pd9HrCBCzB/Bj\n/gU4zrc53D0duxvoLDftuf6/Si8DdaacM1JLdzgO+Evt/rTMrK9v/Fk79HegxfQt\nF6qhAoGAChhEwhTr95S2UEw+9JwKVUC3rTC3IH4unLu2k48Q6pK01nGUYP0EVSD6\n1QEHGdNmSUdyGSAYVFT+p9kbgaXtjy0AdUGNGapREZyI+09X7eCBz7A1swRWSD+g\nYbZ54bknWfUyBENKm/a2sI7+4wcB20atHELAXGyUmLBqrUtT0Gs=\n-----END RSA PRIVATE KEY-----\n', # noqa
        'public_key': b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyC/fG5vnBrGwarNkxgLd\nYEvYcvmRcC9XnW+h/xLtwlGALlVx+1R+MzxcmOTxYzoPAlWKyDlsWp3iNkA0twcR\ny5S5Sz1NilUwVNNWjaPVAbuab/Bo98wVdYHhVc4Jq5honvX/mXp/E+UjWPgWbjrv\nNtRTM+LfeEi5680rA/q5EfPxUr2Z13Z0pr97opGtYCt7Eo0QEIQctQ6t/o2ZDEcv\nCLKV+gCvWZoSgO98uld3hHXdG2W8+DlthJZpZo0kLIDdlVohHNDQfdlTlcTdZwGN\n+KfNIfhCjr9osB1jQiaprDrL2M0wjb3V7CcdS6CQ8xtILAeZJ36R0+DMjZP0Mu+U\nfQIDAQAB\n-----END PUBLIC KEY-----\n', # noqa
    }
}


def get_public_key(appname):
    pem_key = keystore[appname]['public_key']
    return serialization.load_pem_public_key(
        pem_key,
        backend=default_backend())


def get_private_key(appname):
    pem_key = keystore[appname]['private_key']
    return serialization.load_pem_private_key(
        pem_key,
        password=None,
        backend=default_backend())
