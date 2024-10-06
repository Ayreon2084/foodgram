import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from common.enums import FileNames, IngredientFields, TagFields
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Import data from a JSON file into the Ingredient/Tag model.'

    def handle(self, *args, **kwargs):
        try:
            json_file_path = settings.BASE_DIR / 'data'
            self.import_ingredients(
                json_file_path, FileNames.INGREDIENTS.value
            )
            self.import_tags(
                json_file_path, FileNames.TAGS.value
            )
        except Exception as e:
            raise CommandError(f'Error importing data: {e}.')

    def import_ingredients(self, json_file_path, file_name):
        try:
            with open(
                json_file_path / file_name, 'r', encoding='utf-8'
            ) as file:
                ingredients_data = json.load(file)

            ingredients_to_add = []
            for ingredient in ingredients_data:
                name = ingredient.get(
                    IngredientFields.NAME.value
                )
                measurement_unit = ingredient.get(
                    IngredientFields.MEASUREMENT_UNIT.value
                )

                if name and measurement_unit:
                    ingredients_to_add.append(
                        Ingredient(
                            name=name,
                            measurement_unit=measurement_unit
                        )
                    )

            Ingredient.objects.bulk_create(
                ingredients_to_add,
                ignore_conflicts=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully loaded {len(ingredients_to_add)} '
                    'ingredients.'
                )
            )

        except Exception as e:
            raise CommandError(f'Error importing data: {e}')

    def import_tags(self, json_file_path, file_name):

        try:
            with open(
                json_file_path / file_name, 'r', encoding='utf-8'
            ) as file:
                tags_data = json.load(file)

            tags_to_add = []
            for tag in tags_data:
                name = tag.get(
                    TagFields.NAME.value
                )
                slug = tag.get(
                    TagFields.SLUG.value
                )

                if name and slug:
                    tags_to_add.append(
                        Tag(
                            name=name,
                            slug=slug
                        )
                    )

            Tag.objects.bulk_create(
                tags_to_add,
                ignore_conflicts=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully loaded {len(tags_to_add)} tags'
                )
            )

        except Exception as e:
            raise CommandError(f'Error importing data: {e}')
