import os
from pathlib import Path

from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from openai import OpenAI

from movie.models import Movie

_ENV_FILE = Path(__file__).resolve().parent.parent.parent.parent / 'openAI.env'


class Command(BaseCommand):
    help = "Update movie descriptions using OpenAI API"

    def handle(self, *args, **kwargs):
        load_dotenv(_ENV_FILE)
        client = OpenAI(api_key=os.environ.get('openai_apikey'))

        def get_completion(prompt, model="gpt-4o-mini"):
            messages = [{"role": "user", "content": prompt}]
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            return response.choices[0].message.content.strip()

        instruction = (
            "Vas a actuar como un aficionado del cine que sabe describir de forma clara, "
            "concisa y precisa cualquier pelicula en menos de 200 palabras. La descripcion "
            "debe incluir el genero de la pelicula y cualquier informacion adicional que sirva "
            "para crear un sistema de recomendacion."
        )

        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies")

        for movie in movies:
            self.stdout.write(f"Processing: {movie.title}")
            try:
                prompt = (
                    f"{instruction} "
                    f"Vas a actualizar la descripcion '{movie.description}' de la pelicula '{movie.title}'."
                )

                updated_description = get_completion(prompt)
                movie.description = updated_description
                movie.save(update_fields=["description"])

                self.stdout.write(self.style.SUCCESS(f"Updated: {movie.title}"))
            except Exception as e:
                self.stderr.write(f"Failed for {movie.title}: {str(e)}")

            break