from io import BytesIO
import os
from django.core.files import File
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from PIL import Image, ImageOps
from django.conf import settings


LARGE_THUMBNAIL_SIZE = settings.LARGE_THUMBNAIL_SIZE
SMALL_THUMBNAIL_SIZE = settings.SMALL_THUMBNAIL_SIZE
MEDIUM_THUMBNAIL_SIZE = settings.MEDIUM_THUMBNAIL_SIZE


class CompressedImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        if name.split('.')[-1] == 'svg':
            super().save(name, content, save)
            return

        image_format = "WEBP"
        thumbnail_type = (
            MEDIUM_THUMBNAIL_SIZE
            if self.field.is_medium_thumbnail
            else SMALL_THUMBNAIL_SIZE
            if self.field.is_small_thumbnail
            else LARGE_THUMBNAIL_SIZE
            if self.field.is_large_thumbnail
            else MEDIUM_THUMBNAIL_SIZE
        )

        # Compressed Image
        image = Image.open(content)
        image = image.convert('RGBA')
        image = ImageOps.exif_transpose(image)
        image.thumbnail(thumbnail_type)
        im_io = BytesIO()
        image.save(im_io, format=image_format, optimize=True, quality=self.field.quality)

        # Change extension
        filename = os.path.splitext(name)[0]
        filename = f"{filename}.webp"

        image = File(im_io, name=filename)
        super().save(filename, image, save)


class CompressedImageField(models.ImageField):
    attr_class = CompressedImageFieldFile

    def __init__(
            self, verbose_name=None, name=None,
            width_field=None, height_field=None,
            quality=60,
            is_small_thumbnail=False,
            is_medium_thumbnail=False,
            is_large_thumbnail=False,
            **kwargs
    ):
        self.quality = quality
        self.is_small_thumbnail = is_small_thumbnail
        self.is_medium_thumbnail = is_medium_thumbnail
        self.is_large_thumbnail = is_large_thumbnail
        super().__init__(verbose_name, name, width_field, height_field, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.quality:
            kwargs['quality'] = self.quality
        return name, path, args, kwargs
