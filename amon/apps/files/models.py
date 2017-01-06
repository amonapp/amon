import gridfs
import tempfile
from amon.apps.core.basemodel import BaseModel


class FilesModel(BaseModel):
    def __init__(self):
        super(FilesModel, self).__init__()
        self.fs = gridfs.GridFS(self.mongo.get_database(), collection='files')


    def get_by_id(self, file_id=None):
        file_id = self.object_id(file_id)
        
        result = self.fs.get(file_id)

        return result


    def delete(self, file_id=None):
        self.fs.delete(file_id)

    def add(self, file=None, filename=None):
        # Filename is used for temporary files
        filename = filename if filename else file.name
        
        file_id = self.fs.put(file, filename=filename)

        return file_id

    # The file is string, write it to temp
    def add_with_temporary(self, file=None, filename=None):
        file_id = None
        file = "\n".join(file.splitlines()) # Transorm \r\n to \n
        
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(file)
            temp.seek(0)
            
            file_id = files_model.add(temp, filename=filename)
        
            temp.flush()

        return file_id


files_model = FilesModel()