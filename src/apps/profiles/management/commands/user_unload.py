import csv

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from apps.profiles.models.user import User


class Command(BaseCommand):
    help = "Unload users data from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", help="Path to the CSV file")

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        with open(csv_file, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                email = row[0]
                name = row[1]
                surname = row[2]
                phone = row[3]
                password = row[4]

                if User.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f"Duplicate users with email = {email} found"
                        )
                    )
                    self.stdout.write(self.style.ERROR("Data uploading is stopped !!"))
                    break
                user = User.objects.create_user(
                    email=email, phone_number=phone,
                    first_name=name, last_name=surname,
                    password=make_password(password)
                )

                self.stdout.write(self.style.SUCCESS(f'User "{user}" created.'))
        self.stdout.write(self.style.SUCCESS("Data unloading completed."))
