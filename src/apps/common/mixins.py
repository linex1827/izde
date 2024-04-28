class SearchByNameMixin:
    @classmethod
    def search_by_name(cls, request):
        queryset = cls.filter(is_deleted=False)
        name = request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset
