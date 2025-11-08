"""
Serviço de Integração com prescricao.cfm.org.br
Sistema Oficial de Prescrição Eletrônica do CFM
"""
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json


class CFMService:
    """Serviço de integração com o sistema CFM"""
    
    def __init__(self):
        # URL base do sistema CFM
        self.base_url = "https://prescricao.cfm.org.br/api"
        
        # Headers padrão
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Sanaris-Pro/1.0"
        }


# Singleton
cfm_service = CFMService()
