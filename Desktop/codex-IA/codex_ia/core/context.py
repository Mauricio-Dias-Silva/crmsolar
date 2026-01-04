
import os
from pathlib import Path
from typing import List, Dict

class ContextManager:
    def __init__(self, root_path: str):
        self.root = Path(root_path).resolve()
        # Default ignores
        self.ignore_dirs = {'.git', 'venv', '.venv', '__pycache__', '.idea', '.vscode', 'node_modules', 'dist', 'build'}
        self.ignore_exts = {'.pyc', '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.exe', '.dll', '.bin', '.svg', '.ico'}
        self.gitignore_rules = self._load_gitignore()

    def _load_gitignore(self) -> List[str]:
        """Loads patterns from .gitignore if it exists."""
        gitignore_path = self.root / '.gitignore'
        patterns = []
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception:
                pass
        return patterns

    def _is_ignored(self, path: Path) -> bool:
        """Simple check for ignored files/dirs. 
        Note: A robust implementation would use `pathspec` or `gitpython`.
        For now, we check basic names and extensions."""
        
        # Check against basic sets
        if path.name in self.ignore_dirs:
            return True
        if path.suffix in self.ignore_exts:
            return True
            
        # Check if path contains any ignored directory part relative to root
        try:
            rel_path = path.relative_to(self.root)
            for part in rel_path.parts:
                if part in self.ignore_dirs:
                    return True
        except ValueError:
            pass
            
        return False

    def get_context(self) -> str:
        """
        Reads all text files in the project, respecting basic ignore rules.
        """
        buffer = []
        
        for root, dirs, files in os.walk(self.root):
            # Modify dirs in-place to skip ignored directories in os.walk
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if self._is_ignored(file_path):
                    continue
                
                try:
                    # Check size before reading (skip files > 100KB to save tokens)
                    if file_path.stat().st_size > 100 * 1024:
                        buffer.append(f"--- FILE: {file_path.relative_to(self.root)} (SKIPPED - TOO LARGE) ---\n")
                        continue

                    # Try reading as text
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Simple binary check: null bytes
                        if '\0' in content: 
                            continue
                            
                        relative_path = file_path.relative_to(self.root)
                        buffer.append(f"--- FILE: {relative_path} ---\n{content}\n")
                except Exception:
                    continue
                    
        context_str = "\n".join(buffer)
        token_estimate = len(context_str) // 4
        print(f"[Info] Context loaded: ~{token_estimate} tokens")
        return context_str

    def get_file_context(self, file_path: str) -> str:
        """
        Reads a specific file with line numbers for better referencing.
        """
        target_path = Path(file_path).resolve()
        if not target_path.exists():
            return f"Error: File {file_path} not found."
        
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            numbered_lines = []
            for i, line in enumerate(lines, 1):
                numbered_lines.append(f"{i}: {line}")
                
            content = "".join(numbered_lines)
            
            # Retrieve relative path for context
            try:
                rel_path = target_path.relative_to(self.root)
            except ValueError:
                rel_path = target_path.name
                
            return f"--- FILE: {rel_path} ---\n{content}\n"
        except Exception as e:
            return f"Error reading file: {e}"
