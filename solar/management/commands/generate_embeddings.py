# em produtos/management/commands/generate_embeddings.py

import time
import google.generativeai as genai
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from PIL import Image

from produtos.models import ProdutoImage

try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    GEMINI_CONFIGURED = True
except AttributeError:
    GEMINI_CONFIGURED = False

class Command(BaseCommand):
    help = 'Gera e salva os embeddings vetoriais para imagens de produtos usando a API do Gemini.'

    def handle(self, *args, **options):
        if not GEMINI_CONFIGURED:
            self.stdout.write(self.style.ERROR("ERRO: A variável GEMINI_API_KEY não foi configurada ou não foi lida corretamente de settings.py."))
            return

        self.stdout.write(self.style.SUCCESS("Iniciando a geração de embeddings com a API do Gemini..."))

        images_to_process = ProdutoImage.objects.filter(Q(embedding__isnull=True) | Q(embedding__exact=''))

        if not images_to_process.exists():
            self.stdout.write(self.style.WARNING("Nenhuma imagem nova para processar."))
            return

        count = 0
        total = images_to_process.count()

        for produto_image in images_to_process:
            try:
                pil_image = Image.open(produto_image.image.path).convert("RGB")

                response = genai.embed_content(
                    model="models/embedding-001",
                    content=pil_image,
                    task_type="retrieval_document"
                )

                produto_image.embedding = response['embedding']
                produto_image.save(update_fields=['embedding'])

                count += 1
                self.stdout.write(self.style.SUCCESS(f"({count}/{total}) Embedding gerado para: {produto_image.image.name}"))

            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f"ARQUIVO NÃO ENCONTRADO para a imagem ID {produto_image.id}: {produto_image.image.name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao processar imagem ID {produto_image.id} com a API do Gemini: {e}"))
                self.stdout.write(self.style.WARNING("Pausando por 5 segundos antes de tentar novamente..."))
                time.sleep(5) 

            time.sleep(1.1) 

        self.stdout.write(self.style.SUCCESS(f"\nProcesso concluído! {count} embeddings foram gerados com sucesso."))