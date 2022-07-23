from django.core.files.storage import Storage


class MyStorage(Storage):
    def _open(self, name, mode):
        pass

    def _save(self, name, content):
        pass

    def url(self, name):
        return "http://image.meiduo.site:19000/mdfiles/" + name
