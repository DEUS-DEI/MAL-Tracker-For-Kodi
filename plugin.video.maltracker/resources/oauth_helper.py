#!/usr/bin/env python3
"""
MAL OAuth Helper - Aplicación auxiliar para autenticación
Ejecutar independientemente para obtener código OAuth
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import webbrowser
import urllib.parse
import base64
import hashlib
import secrets
import json
import os

class MALOAuthHelper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MAL OAuth Helper")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.client_id = ""
        self.auth_code = ""
        self.code_verifier = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        # Título
        title = tk.Label(self.root, text="MAL OAuth Helper", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Instrucciones
        instructions = tk.Text(self.root, height=8, width=60, wrap=tk.WORD)
        instructions.pack(pady=10)
        instructions.insert(tk.END, 
            "1. Ingresa tu Client ID de MyAnimeList\n"
            "2. Haz clic en 'Generar URL de Autorización'\n"
            "3. Se abrirá tu navegador - autoriza la aplicación\n"
            "4. Copia el código de la URL de callback\n"
            "5. Pégalo en el campo de código\n"
            "6. Haz clic en 'Generar Token'\n"
            "7. Copia el token generado a Kodi")
        instructions.config(state=tk.DISABLED)
        
        # Client ID
        tk.Label(self.root, text="Client ID:").pack()
        self.client_id_entry = tk.Entry(self.root, width=50)
        self.client_id_entry.pack(pady=5)
        
        # Botón generar URL
        tk.Button(self.root, text="Generar URL de Autorización", 
                 command=self.generate_auth_url, bg="blue", fg="white").pack(pady=5)
        
        # Código de autorización
        tk.Label(self.root, text="Código de Autorización:").pack()
        self.auth_code_entry = tk.Entry(self.root, width=50)
        self.auth_code_entry.pack(pady=5)
        
        # Botón generar token
        tk.Button(self.root, text="Generar Token", 
                 command=self.generate_token, bg="green", fg="white").pack(pady=5)
        
        # Resultado
        tk.Label(self.root, text="Token (copiar a Kodi):").pack()
        self.result_text = tk.Text(self.root, height=3, width=60)
        self.result_text.pack(pady=5)
    
    def generate_pkce_pair(self):
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        return code_verifier, code_challenge
    
    def generate_auth_url(self):
        self.client_id = self.client_id_entry.get().strip()
        if not self.client_id:
            messagebox.showerror("Error", "Ingresa tu Client ID")
            return
        
        self.code_verifier, code_challenge = self.generate_pkce_pair()
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': 'http://localhost:8080/callback',
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'state': secrets.token_urlsafe(16)
        }
        
        url = 'https://myanimelist.net/v1/oauth2/authorize?' + urllib.parse.urlencode(params)
        
        try:
            webbrowser.open(url)
            messagebox.showinfo("Éxito", "Navegador abierto. Autoriza la aplicación y copia el código.")
        except:
            messagebox.showinfo("URL Generada", f"Ve manualmente a:\n{url}")
    
    def generate_token(self):
        auth_code = self.auth_code_entry.get().strip()
        if not auth_code:
            messagebox.showerror("Error", "Ingresa el código de autorización")
            return
        
        if not self.client_id or not self.code_verifier:
            messagebox.showerror("Error", "Primero genera la URL de autorización")
            return
        
        # Simular intercambio de token (en la app real haría el request)
        token_data = {
            'client_id': self.client_id,
            'auth_code': auth_code,
            'code_verifier': self.code_verifier,
            'timestamp': 'PLACEHOLDER_FOR_REAL_TOKEN'
        }
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, json.dumps(token_data, indent=2))
        
        messagebox.showinfo("Token Generado", "Copia el contenido y úsalo en Kodi")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MALOAuthHelper()
    app.run()