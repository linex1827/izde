from rest_framework import status

from apps.common.exceptions import UnifiedErrorResponse


class Service:
    model = None

    @classmethod
    def get_or_none(cls, *args, **kwargs):
        try:
            return cls.model.objects.get(*args, **kwargs)
        except cls.model.DoesNotExist:
            return {
                "data": None,
                "message": "Object not found"
            }

    @classmethod
    def get_or_error(cls, model, pk):
        try:
            return model.objects.get(id=pk)
        except model.DoesNotExist:
            raise UnifiedErrorResponse(code=status.HTTP_404_NOT_FOUND, detail="Object not found")

    @classmethod
    def filter(cls, *args, **kwargs):
        return cls.model.objects.filter(*args, **kwargs)

    class Meta:
        abstract = True


def only_objects_decorator(func: callable):
    def only_objects_wrapper(objects, only=(), *args, **kwargs):
        return func(objects, *args, **kwargs).only(*only)

    return only_objects_wrapper


@only_objects_decorator
def get_all_objects(objects):
    return objects.all()


@only_objects_decorator
def filter_objects(objects, user, **kwargs):
    return objects.filter(user, **kwargs)
