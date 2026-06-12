import json

from django.core.management.base import BaseCommand

from ingredients.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из JSON-файла'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к JSON-файлу')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        created = 0
        for item in data:
            _, created_bool = Ingredient.objects.get_or_create(
                name=item['name'],
                measurement_unit=item['measurement_unit'],
            )
            if created_bool:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(f'Загружено: {created} новых ингредиентов')
        )