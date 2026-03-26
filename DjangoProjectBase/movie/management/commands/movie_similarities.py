import os
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Compare two movies and a prompt using OpenAI embeddings and cosine similarity"

    def handle(self, *args, **kwargs):
        # ✅ Load OpenAI API key
        load_dotenv('../openAI.env')
        client = OpenAI(api_key=os.environ.get('openai_apikey'))

        # ✅ Películas seleccionadas para comparar (puedes cambiarlas)
        movie1 = Movie.objects.get(title="Frankenstein")
        movie2 = Movie.objects.get(title="A Trip to the Moon")

        def get_embedding(text):
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)

        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        # ✅ Generar embeddings de las dos películas
        self.stdout.write(f"Generando embeddings para: '{movie1.title}' y '{movie2.title}'...")
        emb1 = get_embedding(movie1.description)
        emb2 = get_embedding(movie2.description)

        # ✅ Calcular similitud entre las dos películas
        similarity = cosine_similarity(emb1, emb2)
        self.stdout.write(f"\n🎬 {movie1.title} vs {movie2.title}: {similarity:.4f}")

        # ✅ Comparar contra un prompt
        prompt = "película de ciencia ficción sobre viajes espaciales y aventuras fantásticas"
        self.stdout.write(f"\nPrompt: \"{prompt}\"")
        prompt_emb = get_embedding(prompt)

        sim_prompt_movie1 = cosine_similarity(prompt_emb, emb1)
        sim_prompt_movie2 = cosine_similarity(prompt_emb, emb2)

        self.stdout.write(f"📝 Similitud prompt vs '{movie1.title}': {sim_prompt_movie1:.4f}")
        self.stdout.write(f"📝 Similitud prompt vs '{movie2.title}': {sim_prompt_movie2:.4f}")

        # ✅ Recomendación
        mejor = movie1.title if sim_prompt_movie1 > sim_prompt_movie2 else movie2.title
        self.stdout.write(self.style.SUCCESS(f"\n✅ Película más recomendada para el prompt: '{mejor}'"))
