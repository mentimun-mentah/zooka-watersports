import os, uuid
from typing import TextIO, Union, Dict
from PIL import Image, ImageOps

class MagicImage:
    FILE_NAME = None
    _BASE_DIR = os.path.join(os.path.dirname(__file__),'../static/')

    def __init__(self,file: Union[TextIO,Dict[str,TextIO]], resize: int, path_upload: str):
        self.file = file
        self.resize = resize
        self.path_upload = path_upload

    def _crop_center(self,pil_img: TextIO, crop_width: int, crop_height: int) -> TextIO:
        img_width, img_height = pil_img.size
        return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

    def _crop_max_square(self,pil_img: TextIO) -> TextIO:
        return self._crop_center(pil_img, min(pil_img.size), min(pil_img.size))

    def _remove_exif_tag(self,pil_img: TextIO) -> TextIO:
        exif = pil_img.getexif()
        # Remove all exif tags
        for k in exif.keys():
            if k != 0x0112:
                exif[k] = None  # If I don't set it to None first (or print it) the del fails for some reason.
                del exif[k]
        # Put the new exif object in the original image
        new_exif = exif.tobytes()
        pil_img.info["exif"] = new_exif
        return pil_img

    def _save_file(self,file: TextIO) -> str:
        # save image
        with Image.open(file) as im:
            # set filename
            ext = im.format.lower()
            filename = uuid.uuid4().hex + '.' + ext
            # crop to center and resize img by 260 x 260
            img = self._crop_max_square(im).resize((self.resize, self.resize), Image.LANCZOS)
            # remove exif tag
            img = self._remove_exif_tag(img)
            # flip image to right path
            img = ImageOps.exif_transpose(img)
            img.save(os.path.join(self._BASE_DIR,self.path_upload,filename))

        return filename

    def save_image(self) -> 'MagicImage':
        if isinstance(self.file,dict):
            # temp storage to save filename in dict
            files_name = dict()
            for index,file in self.file.items():
                filename = self._save_file(file)
                files_name[index] = filename

            self.FILE_NAME = files_name
        else:
            filename = self._save_file(self.file)
            self.FILE_NAME = filename

    @classmethod
    def delete_image(cls,file: str,path_delete: str) -> None:
        path = os.path.join(cls._BASE_DIR,path_delete,file or ' ')
        if os.path.exists(path):
            os.remove(path)
