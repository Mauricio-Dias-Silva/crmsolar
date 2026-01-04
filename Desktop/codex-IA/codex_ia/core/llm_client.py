
import os
from google import genai
from google.genai import types

class GeminiClient:
    def __init__(self):
        # Support both names, prioritize GEMINI_API_KEY
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GENAI_API_KEY")
        
        if not api_key:
            raise ValueError("API Key not found. Please set GEMINI_API_KEY or GENAI_API_KEY in .env")
            
        if "Cole_Sua_Chave" in api_key:
             raise ValueError("API Key appears to be the default placeholder. Please update your .env file with a real key.")
        
        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

    def analyze_architecture(self, context: str) -> str:
        """
        Envia o contexto para o Gemini analisar a arquitetura.
        """
        prompt = f"""
        Você é um Arquiteto de Software Sênior (Codex-IA).
        Analise o seguinte código e sugira 3 melhorias de impacto alto na arquitetura ou legibilidade.
        Seja direto e técnico.

        CONTEXTO:
        {context[:50000]} # Limite de segurança para exemplo
        """
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2, # Baixa temperatura para precisão
            )
        )
        
        return response.text

    def explain_code(self, file_content: str) -> str:
        """
        Explains the logic of a specific file.
        """
        prompt = f"""
        You are a Senior Software Engineer (Codex-IA).
        Explain the functionality of the following file in a clear and didactic way.
        Focus on:
        1. Purpose of the file.
        2. Main classes and functions.
        3. Key logic flows.

        FILE CONTENT:
        {file_content}
        """
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
            )
        )
        return response.text

    def refactor_code(self, file_content: str, instructions: str = "") -> str:
        """
        Suggests refactoring for a specific file.
        """
        prompt = f"""
        You are a Senior Software Engineer (Codex-IA).
        Refactor the following code to improve quality, readability, and performance.
        
        User Instructions: {instructions if instructions else "Apply best practices and clean code principles."}

        FILE CONTENT:
        {file_content}

        Output ONLY the refactored code (or a diff if more appropriate) and a brief summary of changes at the end.
        """
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
            )
        )
        return response.text
