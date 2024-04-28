from rest_framework.schemas.coreapi import AutoSchema
import coreschema
import coreapi


class ObjectCheckSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        api_fields = []
        if method == "GET":
            api_fields = [
                coreapi.Field(
                    name='choice',
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description="updated - created"
                    )
                )
            ]
        return self._manual_fields + api_fields


class PlacementSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        api_fields = []
        if method == "GET":
            api_fields = [
                coreapi.Field(
                    name='name',
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description="(string) search term"
                    )
                )
            ]
        return self._manual_fields + api_fields


class ReviewCheckSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        api_fields = []
        if method == "GET":
            api_fields = [
                coreapi.Field(
                    name='choice',
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description="approved - declined"
                    )
                )
            ]
        return self._manual_fields + api_fields


class VendorOffersSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        api_fields = []
        if method == "GET":
            api_fields = [
                coreapi.Field(
                    name='date',
                    required=False,
                    location="query",
                    schema=coreschema.String(
                        description="choose one: {week, month, half_year, all}"
                    )
                )
            ]
        return self._manual_fields + api_fields
