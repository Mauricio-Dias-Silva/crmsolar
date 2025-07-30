# compras/management/commands/notificar_cupons_expirando.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from compras.models import Cupom
from contas.models import Notificacao # Importe o modelo de Notificacao

class Command(BaseCommand):
    help = 'Verifica cupons que expiram em breve e cria notificações para os usuários.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias_para_expirar',
            type=int,
            default=7, # Padrão: Notificar 7 dias antes da expiração
            help='Número de dias antes da expiração para notificar.',
        )

    def handle(self, *args, **options):
        dias_para_expirar = options['dias_para_expirar']
        
        # Define a data limite para a expiração
        data_limite_inicio = timezone.now().date() + timedelta(days=dias_para_expirar -1) # De hoje + (dias_para_expirar -1)
        data_limite_fim = timezone.now().date() + timedelta(days=dias_para_expirar) # Até hoje + dias_para_expirar (ou seja, se dias_para_expirar=7, verifica cupons que expiram no dia atual + 7 dias)

        # Filtra cupons com status 'disponivel' e que expiram na janela definida
        cupons_expirando = Cupom.objects.filter(
            status='disponivel',
            data_validade__date__gte=data_limite_inicio, # Data de validade maior ou igual ao início da janela
            data_validade__date__lte=data_limite_fim # Data de validade menor ou igual ao fim da janela
        )

        self.stdout.write(f'Verificando cupons que expiram entre {data_limite_inicio} e {data_limite_fim}...')
        
        notificacoes_criadas = 0
        for cupom in cupons_expirando:
            # Verifica se já existe uma notificação recente para este cupom e usuário
            # Você pode ajustar o filtro para ser mais ou menos granular
            notificacao_existente = Notificacao.objects.filter(
                usuario=cupom.usuario,
                titulo=f"Seu cupom {cupom.codigo_cupom} está expirando!",
                data_criacao__date=timezone.now().date() # Evita duplicatas no mesmo dia
            ).exists()

            if not notificacao_existente:
                titulo = f"Seu cupom {cupom.codigo_cupom} está expirando!"
                mensagem = (
                    f"O cupom **{cupom.codigo_cupom}** da oferta **'{cupom.oferta.titulo}'** "
                    f"expira em **{cupom.data_validade.strftime('%d/%m/%Y')}**! "
                    "Não perca a chance de usá-lo."
                )
                link = cupom.oferta.get_absolute_url() # Supondo que a Oferta tenha get_absolute_url() ou construa a URL aqui.
                
                Notificacao.objects.create(
                    usuario=cupom.usuario,
                    titulo=titulo,
                    mensagem=mensagem,
                    link=link,
                    lida=False
                )
                notificacoes_criadas += 1
                self.stdout.write(self.style.SUCCESS(f'Notificação criada para o cupom {cupom.codigo_cupom} do usuário {cupom.usuario.email}.'))
            else:
                self.stdout.write(f'Notificação já existe para o cupom {cupom.codigo_cupom} hoje. Pulando.')

        self.stdout.write(self.style.SUCCESS(f'Total de {notificacoes_criadas} notificações de cupons expirando criadas.'))