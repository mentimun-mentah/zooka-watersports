import os, uuid
from typing import TextIO
from PIL import Image, ImageOps

class MagicImage:
    FILE_NAME = None
    _DIR_AVATAR = os.path.join(os.path.dirname(__file__),'../static/avatars/')

    def __init__(self,value: TextIO):
        self.value = value

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

    def save_image(self) -> 'MagicImage':
        # save image
        with Image.open(self.value) as im:
            # set filename
            ext = im.format.lower()
            filename = uuid.uuid4().hex + '.' + ext
            # crop to center and resize img by 260 x 260
            img = self._crop_max_square(im).resize((260, 260), Image.LANCZOS)
            # remove exif tag
            img = self._remove_exif_tag(img)
            # flip image to right path
            img = ImageOps.exif_transpose(img)
            img.save(os.path.join(self._DIR_AVATAR,filename))

        self.FILE_NAME = filename
