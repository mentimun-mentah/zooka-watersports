import os
from PIL import Image
from marshmallow import Schema, fields, ValidationError

class ImageField(fields.Field):
    _ALLOW_FILE_EXT = ['jpg','png','jpeg']
    _MAX_FILE_SIZE = 4 * 1024 * 1024  # 4 Mb

    def _deserialize(self, value, attr, data, **kwargs):
        if not value:
            raise ValidationError("Missing data for required field.")

        # check valid image
        try:
            with Image.open(value) as img:
                if img.format.lower() not in self._ALLOW_FILE_EXT and img.mode != 'RGB':
                    raise Exception("Image must be {}".format('|'.join(self._ALLOW_FILE_EXT)))
        except Exception as err:
            err = str(err)
            if "cannot identify image file" in err:
                err = "Cannot identify image file"
            raise ValidationError(err)

        # check size image
        value.seek(0,os.SEEK_END)
        size = value.tell()

        if size > self._MAX_FILE_SIZE:
            raise ValidationError("Image cannot grater than 4 Mb")

        value.seek(0)
        # return real image
        return value

class ImageActivitySchema(Schema):
    image = ImageField(required=True)
    image2 = ImageField()
    image3 = ImageField()
    image4 = ImageField()
