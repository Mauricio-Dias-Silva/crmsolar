
import typer
from rich.console import Console
from rich.markdown import Markdown
from codex_ia.core.context import ContextManager
from codex_ia.core.llm_client import GeminiClient
from dotenv import load_dotenv
import os

load_dotenv()

app = typer.Typer()
console = Console()

@app.command()
def audit(path: str = "."):
    """
    Auita o código em busca de melhorias de arquitetura.
    """
    console.print(f"[bold blue]Iniciando auditoria em: {path}[/bold blue]")
    
    context_mgr = ContextManager(path)
    context_data = context_mgr.get_context()
    
    client = GeminiClient()
    analysis = client.analyze_architecture(context_data)
    
    console.print(analysis)

@app.command()
def explain(file_path: str):
    """
    Explica o funcionamento de um arquivo específico.
    """
    console.print(f"[bold green]Lendo arquivo: {file_path}[/bold green]")
    
    context_mgr = ContextManager(".") 
    # Use context_manager relative to current dir, but file_path is passed explicitly
    # Ideally ContextManager should handle the file path resolving relative to root
    # But for now passing '.' as root is safe for CLI usage in project root
    
    file_content = context_mgr.get_file_context(file_path)
    
    if "Error" in file_content:
        console.print(f"[bold red]{file_content}[/bold red]")
        return

    client = GeminiClient()
    with console.status("[bold green]Gerando explicação com Gemini...[/bold green]"):
        explanation = client.explain_code(file_content)
        
    console.print(Markdown(explanation))

@app.command()
def refactor(
    file_path: str, 
    instructions: str = typer.Option("", help="Instruções específicas para refatoração"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Aplica as mudanças diretamente no arquivo")
):
    """
    Sugere refatoração para um arquivo específico. Use --interactive para aplicar.
    """
    console.print(f"[bold blue]Analisando para refatoração: {file_path}[/bold blue]")
    
    context_mgr = ContextManager(".")
    file_content = context_mgr.get_file_context(file_path)
    
    if "Error" in file_content:
        console.print(f"[bold red]{file_content}[/bold red]")
        return

    client = GeminiClient()
    with console.status("[bold blue]Gerando sugestões de refatoração...[/bold blue]"):
        suggestion = client.refactor_code(file_content, instructions)
    
    console.print(Markdown(suggestion))
    
    if interactive:
        # Check if suggestion contains a markdown code block provided by the LLM
        import re
        # Regex to find the LAST code block which usually contains the full refactored code
        # This is a heuristic and might need improvement (e.g. asking LLM for a specific format)
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", suggestion, re.DOTALL)
        
        if not code_blocks:
            console.print("[bold yellow]Não foi possível identificar um bloco de código na resposta para aplicar.[/bold yellow]")
            return
            
        new_code = code_blocks[-1] # Assume the last block is the full code
        
        confirm = typer.confirm("Deseja aplicar estas alterações no arquivo?")
        if confirm:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_code)
                console.print(f"[bold green]Alterações aplicadas com sucesso em {file_path}![/bold green]")
            except Exception as e:
                console.print(f"[bold red]Erro ao salvar arquivo: {e}[/bold red]")
        else:
            console.print("[yellow]Operação cancelada.[/yellow]")

if __name__ == "__main__":
    app()
