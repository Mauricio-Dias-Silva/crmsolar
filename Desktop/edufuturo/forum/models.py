# forum/models.py
from django.db import models
from users.models import CustomUser # Para o autor do tópico e comentário
from courses.models import Lesson, Course # Para relacionar tópico a aula/curso

class Topic(models.Model):
    title = models.CharField("Título", max_length=255)
    content = models.TextField("Conteúdo") # Presumindo que você adicionou este campo

    # Campo 'lesson' - permite que o tópico seja relacionado a uma aula
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='forum_topics',
        verbose_name="Aula Relacionada",
        null=True, blank=True # Permite tópicos gerais ou antes de serem vinculados
    )
    
    # Campo 'course' - opcional, se um tópico puder ser diretamente de um curso sem aula específica
    # Se todo tópico é SEMPRE de uma aula, e a aula já tem um curso, este campo pode ser redundante
    # Mas, para seu list_filter 'lesson__module__course' fazer sentido, Topic precisa de 'lesson'.
    # O filtro 'lesson__module__course' só funciona se Topic tiver um ForeignKey para Lesson.
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_forum_topics', # Renomeado para evitar clash se 'forum_topics' for usado em outro lugar
        verbose_name="Curso",
        null=True, blank=True
    )


    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='authored_forum_topics', # Renomeado para ser único e claro
        verbose_name="Autor"
    )
    
    # Campo 'is_resolved' - para indicar se o tópico foi resolvido
    is_resolved = models.BooleanField("Resolvido", default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tópico"
        verbose_name_plural = "Tópicos"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

# Exemplo de Comment (se ainda não tiver)
class Comment(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='comments', verbose_name="Tópico")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='authored_comments', verbose_name="Autor")
    content = models.TextField("Conteúdo")
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField("Verificado (Professor)", default=False) # Para o admin.py

    # Campo 'parent' para respostas aninhadas (opcional, mas comum em fóruns)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name="Resposta a"
    )

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ['created_at']

    def __str__(self):
        return f"Comentário de {self.author.username} em {self.topic.title}"

# Exemplo de Vote (se ainda não tiver)
class Vote(models.Model):
    # Relaciona o voto a um comentário
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes', verbose_name="Comentário")
    # Relaciona o voto a um usuário
    voter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='votes_given', verbose_name="Eleitor")
    # Pode ser 1 para upvote, -1 para downvote
    value = models.SmallIntegerField("Valor", default=1) # 1 para upvote, -1 para downvote
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Voto"
        verbose_name_plural = "Votos"
        unique_together = ('comment', 'voter') # Um usuário só pode votar uma vez por comentário

    def __str__(self):
        return f"Voto de {self.voter.username} em {self.comment.id}"