import os

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from movie.models import Movie


class Command(BaseCommand):
    help = "Update movie image field from files in media/movie/images/"

    def handle(self, *args, **kwargs):
        images_folder = os.path.join("media", "movie", "images")

        if not os.path.isdir(images_folder):
            self.stderr.write(
                self.style.ERROR(
                    f"Images folder not found: {images_folder}"
                )
            )
            return

        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies in database")

        updated_count = 0
        missing_count = 0

        for movie in movies:
            filename = self._find_image_filename(images_folder, movie.title)
            if not filename:
                self.stderr.write(f"Image not found for: {movie.title}")
                missing_count += 1
                continue

            movie.image = os.path.join("movie", "images", filename)
            movie.save(update_fields=["image"])
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(f"Updated image for: {movie.title}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished. Updated {updated_count} movies, missing images for {missing_count} movies."
            )
        )

    def _find_image_filename(self, images_folder, title):
        # Try common naming conventions used in the workshop resources.
        candidates = []
        candidates.append(f"m_{title}.png")

        windows_safe = "".join("_" if c in '<>:"/\\|?*' else c for c in title)
        candidates.append(f"m_{windows_safe}.png")

        candidates.append(f"m_{slugify(title)}.png")

        for filename in candidates:
            if os.path.exists(os.path.join(images_folder, filename)):
                return filename

        return None