import os
import django
import sys
from datetime import datetime, timedelta
from django.db import IntegrityError, transaction
from django.contrib.auth.hashers import make_password


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# --- Importe seus modelos ---
# A forma recomendada de obter o modelo de usuário é com get_user_model()
from django.contrib.auth import get_user_model
from courses.models import Course, Module, Lesson, Material
from users.models import Student, Professor
from learning.models import Enrollment, LessonProgress
from forum.models import Topic, Comment
from certificates.models import Certificate
from gamification.models import Badge, UserXP, Achievement
from notifications.models import Notification

CustomUser = get_user_model()

# --- Limpa dados anteriores ---
# Usamos transaction.atomic para garantir que a limpeza seja uma operação única e segura.
def reset_data():
    print("🧹 Limpando dados anteriores...")
    with transaction.atomic():
        Certificate.objects.all().delete()
        Achievement.objects.all().delete()
        UserXP.objects.all().delete()
        Notification.objects.all().delete()
        Comment.objects.all().delete()
        Topic.objects.all().delete()
        LessonProgress.objects.all().delete()
        Enrollment.objects.all().delete()
        Student.objects.all().delete()
        Professor.objects.all().delete()
        Material.objects.all().delete()
        Lesson.objects.all().delete()
        Module.objects.all().delete()
        Course.objects.all().delete()
        Badge.objects.all().delete()
        CustomUser.objects.filter(is_superuser=False).delete()
    print("✅ Dados anteriores removidos.")

@transaction.atomic
def run_seed_data():
    """
    Função principal para popular o banco de dados com dados iniciais.
    """
    print("🚀 Populando o EduFuturo com dados completos...")
    
    reset_data()

    # === 1. CRIAR USUÁRIOS E PERFIS ===
    print("👥 Criando usuários e perfis...")

    # Superusuário Admin
    admin_user, created_user = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@edufuturo.org',
            'first_name': 'Admin',
            'last_name': 'EduFuturo',
            'role': CustomUser.Role.ADMIN,
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created_user:
        admin_user.set_password('123')
        admin_user.save()
        print("🔐 Superusuário 'admin' criado (senha: 123)")
    else:
        print("⚠️ Superusuário 'admin' já existe.")

    # Professor
    prof_davi_user, created_user = CustomUser.objects.get_or_create(
        username='prof_davi',
        defaults={
            'email': 'davi@edufuturo.org',
            'password': make_password('123'),
            'first_name': 'Davi',
            'last_name': 'Silva',
            'role': CustomUser.Role.PROFESSOR # <-- AQUI ESTÁ A CORREÇÃO
        }
    )
    if created_user:
        print(f"✅ Usuário 'prof_davi' criado.")
    
    professor_davi_profile, created_profile = Professor.objects.get_or_create(
        user=prof_davi_user
    )
    if created_profile:
        print(f"👨‍🏫 Perfil Professor para 'prof_davi' criado.")
    else:
        print(f"⚠️ Perfil Professor para 'prof_davi' já existe.")

    # Aluno Julia
    aluno_julia_user, created_user = CustomUser.objects.get_or_create(
        username='aluno_julia',
        defaults={
            'email': 'julia@edufuturo.org',
            'password': make_password('123'),
            'first_name': 'Julia',
            'last_name': 'Pereira',
            'role': CustomUser.Role.STUDENT
        }
    )
    if created_user:
        print(f"✅ Usuário 'aluno_julia' criado.")
    
    student_julia_profile, created_profile = Student.objects.get_or_create(
        user=aluno_julia_user,
        defaults={
            'enrollment_number': 'STD000001'
        }
    )
    if created_profile:
        print(f"🎓 Perfil Aluno para 'aluno_julia' criado.")
    else:
        print(f"⚠️ Perfil Aluno para 'aluno_julia' já existe.")

    # Aluno Carlos
    aluno_carlos_user, created_user = CustomUser.objects.get_or_create(
        username='aluno_carlos',
        defaults={
            'email': 'carlos@edufuturo.org',
            'password': make_password('123'),
            'first_name': 'Carlos',
            'last_name': 'Oliveira',
            'role': CustomUser.Role.STUDENT
        }
    )
    if created_user:
        print(f"✅ Usuário 'aluno_carlos' criado.")
        
    student_carlos_profile, created_profile = Student.objects.get_or_create(
        user=aluno_carlos_user,
        defaults={
            'enrollment_number': 'STD000002'
        }
    )
    if created_profile:
        print(f"🎓 Perfil Aluno para 'aluno_carlos' criado.")
    else:
        print(f"⚠️ Perfil Aluno para 'aluno_carlos' já existe.")

    # === 2. CRIAR CURSO COMPLETO ===
    print("\n📚 Criando curso 'Introdução ao Python'...")
    curso, created_course = Course.objects.get_or_create(
        code='PY101',
        defaults={
            'name': 'Introdução ao Python',
            'description': 'Aprenda os fundamentos da linguagem Python do zero.',
            'workload_hours': 40,
            'start_date': '2025-08-01',
            'end_date': '2025-10-01',
            'is_active': True
        }
    )
    if created_course:
        curso.professors.add(prof_davi_user)
        print(f"✅ Curso '{curso.name}' criado com o professor {professor_davi_profile.user.get_full_name()}")
    else:
        print(f"⚠️ Curso '{curso.name}' já existe.")

    # Módulo 1
    modulo1, created_module = Module.objects.get_or_create(
        course=curso,
        order=1,
        defaults={
            'title': 'Fundamentos de Python',
            'description': 'Variáveis, tipos, estruturas de controle'
        }
    )
    if created_module: print(f"✅ Módulo '{modulo1.title}' criado para '{curso.name}'.")
    else: print(f"⚠️ Módulo '{modulo1.title}' já existe para '{curso.name}'.")

    # Aula 1
    aula1, created_lesson = Lesson.objects.get_or_create(
        module=modulo1,
        order=1,
        defaults={
            'title': 'Variáveis e Tipos de Dados',
            'content': 'Nesta aula, você aprenderá a declarar variáveis e trabalhar com tipos como int, float, str e bool.',
            'duration_minutes':15,
            'video_url': 'https://www.youtube.com/watch?v=hasRy5ugJ6w'
        }
    )
    if created_lesson: print(f"✅ Aula '{aula1.title}' criada para '{modulo1.title}'.")
    else: print(f"⚠️ Aula '{aula1.title}' já existe para '{modulo1.title}'.")

    # Material da aula
    material1, created_material = Material.objects.get_or_create(
        lesson=aula1,
        title='Exercícios de Variáveis',
        defaults={
            'file': 'materials/exercicios_python.pdf'
        }
    )
    if created_material: print(f"✅ Material 'Exercícios de Variáveis' criado.")
    else: print(f"⚠️ Material 'Exercícios de Variáveis' já existe.")
    
    # Aula 2
    aula2, created_lesson = Lesson.objects.get_or_create(
        module=modulo1,
        order=2,
        defaults={
            'title': 'Estruturas de Controle',
            'content': 'If, else, for, while.',
            'duration_minutes':15,
            'video_url': 'https://www.youtube.com/watch?v=7I5ZWLvP87k'
        }
    )
    if created_lesson: print(f"✅ Aula '{aula2.title}' criada para '{modulo1.title}'.")
    else: print(f"⚠️ Aula '{aula2.title}' já existe para '{modulo1.title}'.")

    # === 3. MATRÍCULA E PROGRESSO ===
    print("\n📈 Matriculando alunos e simulando progresso...")
    
    enrollment_julia, created_enrollment = Enrollment.objects.get_or_create(
        student=student_julia_profile,
        course=curso
    )
    if created_enrollment: print(f"✅ Aluno 'Julia' matriculado no curso.")
    else: print(f"⚠️ Aluno 'Julia' já está matriculado no curso.")

    enrollment_carlos, created_enrollment = Enrollment.objects.get_or_create(
        student=student_carlos_profile,
        course=curso
    )
    if created_enrollment: print(f"✅ Aluno 'Carlos' matriculado no curso.")
    else: print(f"⚠️ Aluno 'Carlos' já está matriculado no curso.")

    # Julia assistiu às duas aulas
    lp1, created_lp = LessonProgress.objects.get_or_create(
        student=student_julia_profile,
        lesson=aula1,
        defaults={
            'completed': True,
            'completed_at': datetime.now() - timedelta(days=2),
            'time_spent': timedelta(minutes=15)
        }
    )
    if created_lp: print(f"✅ Progresso de Julia na aula 1 simulado.")
    else: print(f"⚠️ Progresso de Julia na aula 1 já existe.")
    
    lp2, created_lp = LessonProgress.objects.get_or_create(
        student=student_julia_profile,
        lesson=aula2,
        defaults={
            'completed': True,
            'completed_at': datetime.now() - timedelta(days=1),
            'time_spent': timedelta(minutes=20)
        }
    )
    if created_lp: print(f"✅ Progresso de Julia na aula 2 simulado.")
    else: print(f"⚠️ Progresso de Julia na aula 2 já existe.")

    # Carlos assistiu só a primeira
    lp3, created_lp = LessonProgress.objects.get_or_create(
        student=student_carlos_profile,
        lesson=aula1,
        defaults={
            'completed': True,
            'completed_at': datetime.now() - timedelta(days=3),
            'time_spent': timedelta(minutes=15)
        }
    )
    if created_lp: print(f"✅ Progresso de Carlos na aula 1 simulado.")
    else: print(f"⚠️ Progresso de Carlos na aula 1 já existe.")

    # === 4. FÓRUM ===
    print("\n💬 Criando tópicos e comentários no fórum...")

    topic, created_topic = Topic.objects.get_or_create(
        lesson=aula1,
        author=aluno_carlos_user,
        defaults={
            'title': 'Dúvida sobre variáveis',
            'content': 'Como declarar uma variável que armazena texto?'
        }
    )
    if created_topic: print("✅ Tópico 'Dúvida sobre variáveis' criado.")
    else: print("⚠️ Tópico 'Dúvida sobre variáveis' já existe.")
    
    comment_prof, created_comment = Comment.objects.get_or_create(
        topic=topic,
        author=prof_davi_user,
        defaults={
            'content': 'Você usa aspas: nome = "João". Isso cria uma string.',
            'is_verified': True
        }
    )
    if created_comment: print("✅ Comentário do professor criado.")
    else: print("⚠️ Comentário do professor já existe.")
    
    comment_julia, created_comment = Comment.objects.get_or_create(
        topic=topic,
        author=aluno_julia_user,
        defaults={
            'content': 'Obrigada, professor! Agora entendi.'
        }
    )
    if created_comment: print("✅ Comentário de Julia criado.")
    else: print("⚠️ Comentário de Julia já existe.")

    # === 5. CERTIFICADO (Julia completou 100%) ===
    print("\n📜 Emitindo certificado para Julia...")
    
    cert, created_cert = Certificate.objects.get_or_create(
        student=student_julia_profile,
        course=curso
    )
    if created_cert: print(f"✅ Certificado emitido.")
    else: print(f"⚠️ Certificado já existe.")

    # === 6. GAMIFICAÇÃO ===
    print("\n🎮 Aplicando gamificação...")
    
    badge_concluiu, created_badge = Badge.objects.get_or_create(
        name=f"Concluiu: {curso.name[:15]}",
        defaults={
            "description": f"Concluiu o curso {curso.name}",
            "icon": "bi-award",
            "xp_value": 100
        }
    )
    if created_badge: print(f"✅ Badge '{badge_concluiu.name}' criado.")
    else: print(f"⚠️ Badge '{badge_concluiu.name}' já existe.")

    achievement_julia_concluiu, created_ach = Achievement.objects.get_or_create(
        user=aluno_julia_user,
        badge=badge_concluiu,
        course=curso
    )
    if created_ach: print(f"✅ Julia ganhou a badge '{badge_concluiu.name}'.")
    else: print(f"⚠️ Julia já tem a badge '{badge_concluiu.name}'.")
    
    badge_iniciante, created_badge = Badge.objects.get_or_create(
        name="Iniciante",
        defaults={
            "description": "Concluiu a primeira aula",
            "icon": "bi-play-btn",
            "xp_value": 20
        }
    )
    if created_badge: print(f"✅ Badge '{badge_iniciante.name}' criado.")
    else: print(f"⚠️ Badge '{badge_iniciante.name}' já existe.")
    
    achievement_julia_iniciante, created_ach = Achievement.objects.get_or_create(
        user=aluno_julia_user,
        badge=badge_iniciante,
        defaults={'course': curso}
    )
    if created_ach: print(f"✅ Julia ganhou a badge '{badge_iniciante.name}'.")
    else: print(f"⚠️ Julia já tem a badge '{badge_iniciante.name}'.")

    # XP total
    xp_julia, created_xp = UserXP.objects.get_or_create(user=aluno_julia_user)
    if xp_julia.total_xp == 0:
        xp_julia.total_xp = 120 # Iniciante + Concluinte
        xp_julia.save()
        print("✅ XP de Julia atualizado.")
    else:
        print("⚠️ XP de Julia já está atualizado.")
        
    print("✅ Gamificação aplicada")

    # === 7. NOTIFICAÇÕES ===
    print("\n🔔 Enviando notificações...")

    # O script assume que você criou os objetos 'topic' e 'cert'
    # mas o 'created_notification' não foi definido no escopo
    notification_forum, created_notification = Notification.objects.get_or_create(
        recipient=aluno_julia_user,
        target=topic,
        defaults={
            'verb': "respondeu sua pergunta no fórum",
            'notification_type': "forum_reply"
        }
    )
    if created_notification: print("✅ Notificação de fórum criada para Julia.")
    else: print("⚠️ Notificação de fórum para Julia já existe.")

    notification_cert, created_notification = Notification.objects.get_or_create(
        recipient=aluno_julia_user,
        target=cert,
        defaults={
            'verb': "Parabéns! Você concluiu o curso e recebeu um certificado.",
            'notification_type': "success"
        }
    )
    if created_notification: print("✅ Notificação de certificado criada para Julia.")
    else: print("⚠️ Notificação de certificado para Julia já existe.")

    print("✅ Notificações criadas")

    # === FIM ===
    print("\n🎉 POPULAÇÃO COMPLETA!")

if __name__ == '__main__':
    run_seed_data()