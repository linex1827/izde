import csv
from django.core.management.base import BaseCommand

from apps.houserent.models import ObjectKind, ObjectType, ObjectFacility, Location, LocationObject, Vendor


class Command(BaseCommand):
    help = "Unload locations data from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", help="Path to the CSV file")

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        with open(csv_file, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                location = row[0]
                vendor = row[1]
                name = row[2]
                description = row[3]
                room_quantity = row[4]
                occupancy = row[5]
                facilities = row[6].split(";")
                object_type = row[7]
                object_kind = row[8]
                rules = row[9]
                cancellation_policy = row[10]

                if LocationObject.objects.filter(name=name).exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f"Duplicate objects with name = {name} found"
                        )
                    )
                    self.stdout.write(self.style.ERROR("Data uploading is stopped !!"))
                    break
                lcation = Location.objects.filter(name=location).first()
                vndor = Vendor.objects.filter(email=vendor).first()
                obj_kind, _ = ObjectKind.objects.get_or_create(name=object_kind)
                obj_type, _ = ObjectType.objects.get_or_create(name=object_type)
                object = LocationObject.objects.create(
                    name=name, location=lcation, vendor=vndor, description=description,
                    room_quantity=room_quantity, occupancy=occupancy, object_type=obj_type,
                    object_kind=obj_kind, rules=rules, cancellation_policy=cancellation_policy
                )
                for facility_name in facilities:
                    facility, created = ObjectFacility.objects.get_or_create(name=facility_name.strip())
                    object.facility.add(facility)

                self.stdout.write(self.style.SUCCESS(f'Object "{object}" created.'))
        self.stdout.write(self.style.SUCCESS("Data unloading completed."))
