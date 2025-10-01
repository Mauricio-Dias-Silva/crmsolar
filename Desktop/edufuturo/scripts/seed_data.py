import os
import django
import sys

# Adiciona o diretório raiz do projeto ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django.setup()

# Agora importe seus modelos
from courses.models import Course, Module, Lesson
from users.models import CustomUser, Student, Professor

# Cria superusuário (se não existir)
if not CustomUser.objects.filter(username='admin').exists():
    admin = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@edufuturo.org',
        password='123',
        first_name='Admin',
        last_name='EduFuturo'
    )
    print("Superusuário criado.")

# Cria usuários de exemplo
professor = CustomUser.objects.create_user(
    username='prof_davi',
    email='davi@edufuturo.org',
    password='123',
    first_name='Davi',
    last_name='Silva',
    role='PROFESSOR'
)
Professor.objects.get_or_create(user=professor)

aluno = CustomUser.objects.create_user(
    username='aluno_julia',
    email='julia@edufuturo.org',
    password='123',
    first_name='Julia',
    last_name='Pereira',
    role='STUDENT'
)
Student.objects.get_or_create(user=aluno, defaults={'enrollment_number': 'STD000001'})

# Cria curso
curso = Course.objects.create(
    name='Introdução ao Python',
    code='PY101',
    description='Aprenda os fundamentos da linguagem Python.',
    workload_hours=40,
    start_date='2025-08-01',
    end_date='2025-10-01',
    is_active=True
)
curso.professors.add(professor)

# Cria módulo
modulo = Module.objects.create(
    course=curso,
    title='Fundamentos de Python',
    order=1
)

# Cria aula
Lesson.objects.create(
    module=modulo,
    title='Variáveis e Tipos',
    content='Aprenda a declarar variáveis em Python.',
    duration_minutes=15,
    video_url='https://www.youtube.com/watch?v=hasRy5ugJ6w'
)

print("✅ Dados populados com sucesso!")