class UsernameConverter:
    regex = r"[a-zA-z0-9_-]{5,20}"

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)


class MobileConverter:
    regex = r"1[3-9]\d{9}"

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)
