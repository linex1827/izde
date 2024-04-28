from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password


class CustomUserManager(BaseUserManager):
    def create_user(self, email, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        user_type = self.model(email=email, **extra_fields)
        user_type.is_active = True
        user_type.save(using=self._db)
        return user_type

    def create_superuser(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        super_user = self.model(email=email, **extra_fields)
        super_user.is_active = True
        super_user.password = make_password(password)
        super_user.save(using=self._db)
        return super_user

