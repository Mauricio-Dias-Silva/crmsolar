# Codex-IA 🧠

**Assistente de Codificação Inteligente (CLI)**

Ferramenta de linha de comando que utiliza o **Gemini 3 Pro** para ler o contexto do seu projeto local, sugerir refatorações, explicar código e automatizar tarefas.

## Funcionalidades
*   **Contexto Inteligente:** Lê arquivos locais para entender a estrutura do projeto, respeitando `.gitignore`.
*   **Refatoração:** Sugere melhorias de código e aplica correções automaticamente com `--interactive`.
*   **Explicação:** Descreve o funcionamento lógico de arquivos e módulos.

## Instalação

```bash
pip install -e .
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:
```env
GEMINI_API_KEY=sua_chave_aqui
```

## Uso

### Explicação de Código
Entenda o que um arquivo faz:
```bash
python -m codex_ia.main explain codex_ia/core/context.py
```

### Refatoração
Receba sugestões de melhoria:
```bash
python -m codex_ia.main refactor codex_ia/main.py
```

### Refatoração Interativa
Aplique as mudanças sugeridas diretamente:
```bash
python -m codex_ia.main refactor codex_ia/main.py --interactive
```

### Problemas Comuns
Se o comando `codex` não for encontrado, use `python -m codex_ia.main` conforme os exemplos acima.
