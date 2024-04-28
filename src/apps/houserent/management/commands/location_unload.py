import csv
from django.core.management.base import BaseCommand

from apps.houserent.models import Location, LocationFacility, Placement


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
                name = row[0]
                placement = row[1]
                street = row[2]
                house = row[3]
                address_link = row[4]
                facilities = row[5].split(";")
                rules = row[6]

                if Location.objects.filter(name=name).exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f"Duplicate locations with name = {name} found"
                        )
                    )
                    self.stdout.write(self.style.ERROR("Data uploading is stopped !!"))
                    break
                if Placement.objects.filter(name=placement).exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f"Duplicate placements with name = {name} found"
                        )
                    )
                    self.stdout.write(self.style.ERROR("Data uploading is stopped !!"))
                    break
                placement_object, created_placement = Placement.objects.get_or_create(name=placement)
                location = Location.objects.create(
                    name=name, placement=placement_object, street=street, house=house, address_link=address_link, rules=rules,
                )
                for facility_name in facilities:
                    facility, created = LocationFacility.objects.get_or_create(name=facility_name.strip())
                    location.facility.add(facility)

                self.stdout.write(self.style.SUCCESS(f'Location "{location}" created.'))
        self.stdout.write(self.style.SUCCESS("Data unloading completed."))
