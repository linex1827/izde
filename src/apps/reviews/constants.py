from django.utils.translation import gettext_lazy as _


REVIEW_STATUS_CHOICE = (
        ("approved", _("Одобрено")),
        ("declined", _("Отклонено")),
    )

STARS_CHOICE = ([(i, "★" * i) for i in range(1, 6)])
