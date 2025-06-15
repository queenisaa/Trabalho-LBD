# Este módulo cuida exclusivamente da interação com a API do Google.

import os
import base64
from email.mime.text import MIMEText

from flask import flash, redirect, url_for
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def enviar_email_otp(destinatario, nome_usuario, otp):
    """
    Gera as credenciais do Google, envia um e-mail com o código OTP e
    cuida do fluxo de autorização. Retorna True em caso de sucesso, False em caso de falha.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Erro ao atualizar token, forçando novo login: {e}")
                if os.path.exists('token.json'):
                    os.remove('token.json')
                creds = None
        
        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=8080)
            except Exception as e:
                print(f"Falha ao iniciar o fluxo de autorização: {e}")
                flash("Não foi possível iniciar a autenticação com o Google. Verifique o arquivo credentials.json.", "danger")
                return False

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        corpo_email = f"Olá, {nome_usuario}.\n\nSeu código de acesso para o Banco Malvader é: {otp}\n\nEste código expira em 10 minutos."
        message = MIMEText(corpo_email)
        message['To'] = destinatario
        message['Subject'] = "Seu Código de Acesso - Banco Malvader"
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        service.users().messages().send(userId="me", body=create_message).execute()
        print(f"E-mail com OTP enviado para {destinatario}.")
        return True
    except (HttpError, ValueError) as error:
        print(f'Ocorreu um erro ao enviar o e-mail ou na autorização: {error}')
        flash("Ocorreu um problema com o serviço de e-mail. Tente novamente.", "danger")
        return False
