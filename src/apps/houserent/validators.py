from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone


class HouseRentValidator:
    @staticmethod
    def validate_dates(start_date, end_date):
        today = timezone.datetime.now().date()
        errors = {}

        if start_date > end_date:
            errors["start_date"] = _("Дата начала должна быть раньше даты окончания.")
            errors["end_date"] = _("Дата окончания должна быть позже даты начала.")

        if start_date < today:
            errors["start_date"] = _("Дата начала не может быть в прошлом.")

        if errors:
            raise ValidationError(errors)

    @staticmethod
    def validate_times(check_in, check_out):
        if check_in <= check_out:
            raise ValidationError(
                {
                    "check_in": _("Время заезда должно быть позже времени выезда."),
                    "check_out": _("Время выезда должно быть раньше времени заезда."),
                }
            )

    @staticmethod
    def validate_unique_names_for_objects(id, name, vendor_id):
        from apps.houserent.models import LocationObject

        if (
            LocationObject.objects.filter(name=name, vendor_id=vendor_id)
            .exclude(id=id)
            .exists()
        ):
            raise ValidationError(
                _("Объект с таким именем уже существует у данного вендора.")
            )

    @staticmethod
    def check_placement(value):
        possible_patterns = [
            "город", "село", "поселок", "область", "район"
        ]
        value_words = value.lower().split()
        if not any(pattern in value_words for pattern in possible_patterns):
            patterns_str = ", ".join(possible_patterns)
            raise ValidationError(
                {
                    "name": _(f"Название должно содержать одно из следующих значений: {patterns_str}")
                }
            )
