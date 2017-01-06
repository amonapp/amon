from amon.apps.core.basemodel import BaseModel


class BookmarksModel(BaseModel):

    def __init__(self):
        super(BookmarksModel, self).__init__()
        self.collection = self.mongo.get_collection('bookmarks')


    def create(self, data=None):
        result = self.insert(data)


        self.collection.ensure_index([('type', self.desc)], background=True)

        return result

bookmarks_model = BookmarksModel()