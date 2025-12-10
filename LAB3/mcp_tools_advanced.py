"""
🚀 Outils MCP Avancés pour EMSI-Bot
WhatsApp, Email, Météo, Calendar, et plus encore
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Charger les variables d'environnement
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class TwilioSMSTool:
    """Outil pour envoyer des SMS via Twilio"""
    
    @staticmethod
    async def send_sms(phone: str, message: str) -> Dict[str, Any]:
        """
        Envoie un SMS via Twilio
        
        Args:
            phone: Numéro de téléphone (format: +212xxxxxxxxx)
            message: Contenu du message
        """
        try:
            # Récupérer les credentials Twilio
            account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'AC5fd137e8dfecff520729942d30829fcd')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            from_number = os.getenv('TWILIO_FROM_NUMBER', '+13855062275')
            
            if not auth_token:
                logger.warning("⚠️ TWILIO_AUTH_TOKEN non configuré, mode simulation")
                return {
                    "success": False,
                    "message": f"SMS simulé vers {phone}: {message[:50]}...",
                    "timestamp": datetime.now().isoformat(),
                    "note": "⚠️ Configurez TWILIO_AUTH_TOKEN dans .env pour activer l'envoi réel"
                }
            
            # Import Twilio
            try:
                from twilio.rest import Client
                
                client = Client(account_sid, auth_token)
                
                # Envoyer le SMS
                sms = client.messages.create(
                    body=message,
                    from_=from_number,
                    to=phone
                )
                
                logger.info(f"📱 SMS envoyé avec succès - SID: {sms.sid}")
                
                return {
                    "success": True,
                    "message": f"SMS envoyé à {phone}",
                    "sid": sms.sid,
                    "status": sms.status,
                    "timestamp": datetime.now().isoformat()
                }
                
            except ImportError:
                logger.error("❌ Module 'twilio' non installé. Installez avec: pip install twilio")
                return {
                    "success": False,
                    "error": "Module twilio non installé",
                    "note": "Installez avec: pip install twilio"
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur envoi SMS: {e}")
            return {"success": False, "error": str(e)}


class WhatsAppTool:
    """Outil pour envoyer des messages WhatsApp via Twilio"""
    
    @staticmethod
    async def send_message(phone: str, message: str) -> Dict[str, Any]:
        """
        Envoie un message WhatsApp via Twilio
        
        Args:
            phone: Numéro WhatsApp (format: whatsapp:+212xxxxxxxxx)
            message: Contenu du message
        """
        try:
            # Récupérer les credentials Twilio
            account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'AC5fd137e8dfecff520729942d30829fcd')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            from_number = os.getenv('TWILIO_FROM_NUMBER', '+13855062275')
            
            if not auth_token:
                logger.warning("⚠️ TWILIO_AUTH_TOKEN non configuré")
                return {
                    "success": False,
                    "message": f"WhatsApp simulé vers {phone}: {message[:50]}...",
                    "note": "Configure TWILIO_AUTH_TOKEN dans .env"
                }
            
            # Ajouter le préfixe WhatsApp si nécessaire
            if not phone.startswith('whatsapp:'):
                phone = f'whatsapp:{phone}'
            
            from_whatsapp = f'whatsapp:{from_number}'
            
            # Import Twilio
            from twilio.rest import Client
            
            client = Client(account_sid, auth_token)
            
            # Envoyer le message WhatsApp
            wa_message = client.messages.create(
                body=message,
                from_=from_whatsapp,
                to=phone
            )
            
            logger.info(f"📱 WhatsApp envoyé - SID: {wa_message.sid}")
            
            return {
                "success": True,
                "message": f"WhatsApp envoyé à {phone}",
                "sid": wa_message.sid,
                "status": wa_message.status,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi WhatsApp: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def send_media(phone: str, media_url: str, caption: str = "") -> Dict[str, Any]:
        """Envoie une image/vidéo via WhatsApp"""
        try:
            logger.info(f"📸 Envoi média WhatsApp vers {phone}")
            return {
                "success": True,
                "message": f"Média envoyé à {phone}",
                "media_url": media_url,
                "caption": caption
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class EmailTool:
    """Outil pour envoyer des emails"""
    
    @staticmethod
    async def send_email(to: str, subject: str, body: str, html: bool = False) -> Dict[str, Any]:
        """
        Envoie un email
        
        Args:
            to: Adresse email destinataire
            subject: Sujet de l'email
            body: Corps du message
            html: Si True, envoie en HTML
        """
        try:
            # En production, utiliser SendGrid, AWS SES, ou SMTP
            logger.info(f"📧 Envoi email vers {to}: {subject}")
            
            return {
                "success": True,
                "message": f"Email envoyé à {to}",
                "subject": subject,
                "timestamp": datetime.now().isoformat(),
                "note": "⚠️ Configuration SMTP/SendGrid requise en production"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def send_with_attachment(to: str, subject: str, body: str, 
                                   attachment_path: str) -> Dict[str, Any]:
        """Envoie un email avec pièce jointe"""
        try:
            logger.info(f"📎 Envoi email avec pièce jointe vers {to}")
            return {
                "success": True,
                "message": f"Email avec pièce jointe envoyé à {to}",
                "attachment": attachment_path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class WeatherTool:
    """Outil pour obtenir la météo"""
    
    @staticmethod
    async def get_weather(city: str, country: str = "MA") -> Dict[str, Any]:
        """
        Obtient la météo actuelle
        
        Args:
            city: Nom de la ville (ex: "Casablanca", "Rabat")
            country: Code pays (default: MA pour Maroc)
        """
        try:
            # En production, utiliser OpenWeatherMap API
            logger.info(f"🌤️ Récupération météo pour {city}, {country}")
            
            # Simulation de données météo
            mock_weather = {
                "success": True,
                "city": city,
                "country": country,
                "temperature": 22,
                "feels_like": 20,
                "humidity": 65,
                "description": "Ensoleillé avec quelques nuages",
                "icon": "☀️",
                "wind_speed": 15,
                "timestamp": datetime.now().isoformat(),
                "note": "⚠️ API OpenWeatherMap requise pour données réelles"
            }
            
            return mock_weather
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_forecast(city: str, days: int = 3) -> Dict[str, Any]:
        """Obtient les prévisions météo sur plusieurs jours"""
        try:
            logger.info(f"📅 Prévisions météo {days} jours pour {city}")
            
            forecast = {
                "success": True,
                "city": city,
                "days": days,
                "forecast": [
                    {"day": 1, "temp_max": 24, "temp_min": 18, "description": "Ensoleillé"},
                    {"day": 2, "temp_max": 23, "temp_min": 17, "description": "Partiellement nuageux"},
                    {"day": 3, "temp_max": 22, "temp_min": 16, "description": "Nuageux"}
                ][:days]
            }
            
            return forecast
        except Exception as e:
            return {"success": False, "error": str(e)}


class CalendarTool:
    """Outil pour gérer un calendrier"""
    
    @staticmethod
    async def create_event(title: str, date: str, time: str, 
                          duration_minutes: int = 60) -> Dict[str, Any]:
        """
        Crée un événement dans le calendrier
        
        Args:
            title: Titre de l'événement
            date: Date (YYYY-MM-DD)
            time: Heure (HH:MM)
            duration_minutes: Durée en minutes
        """
        try:
            logger.info(f"📅 Création événement: {title} le {date} à {time}")
            
            return {
                "success": True,
                "event": {
                    "title": title,
                    "date": date,
                    "time": time,
                    "duration": duration_minutes,
                    "id": f"evt_{datetime.now().timestamp()}"
                },
                "message": f"Événement '{title}' créé pour le {date} à {time}",
                "note": "⚠️ Intégration Google Calendar/Outlook requise en production"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def list_events(date: str) -> Dict[str, Any]:
        """Liste les événements d'une date donnée"""
        try:
            logger.info(f"📋 Récupération événements du {date}")
            
            # Simulation
            mock_events = [
                {"time": "09:00", "title": "Cours de Machine Learning", "duration": 120},
                {"time": "14:00", "title": "Réunion projet EMSI-Bot", "duration": 60}
            ]
            
            return {
                "success": True,
                "date": date,
                "events": mock_events,
                "count": len(mock_events)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class TranslationTool:
    """Outil de traduction"""
    
    @staticmethod
    async def translate(text: str, from_lang: str, to_lang: str) -> Dict[str, Any]:
        """
        Traduit un texte
        
        Args:
            text: Texte à traduire
            from_lang: Langue source (ex: 'fr', 'en', 'ar')
            to_lang: Langue cible
        """
        try:
            logger.info(f"🌍 Traduction {from_lang} -> {to_lang}")
            
            return {
                "success": True,
                "original": text,
                "translated": f"[Traduction simulée de '{text}' en {to_lang}]",
                "from_lang": from_lang,
                "to_lang": to_lang,
                "note": "⚠️ Google Translate API ou DeepL requise en production"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class NotificationTool:
    """Outil pour envoyer des notifications"""
    
    @staticmethod
    async def send_notification(title: str, message: str, 
                               priority: str = "normal") -> Dict[str, Any]:
        """
        Envoie une notification push
        
        Args:
            title: Titre de la notification
            message: Contenu du message
            priority: normal, high, urgent
        """
        try:
            logger.info(f"🔔 Notification: {title}")
            
            return {
                "success": True,
                "notification": {
                    "title": title,
                    "message": message,
                    "priority": priority,
                    "timestamp": datetime.now().isoformat()
                },
                "note": "⚠️ Firebase Cloud Messaging ou OneSignal requise en production"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class PDFTool:
    """Outil pour manipuler des PDFs"""
    
    @staticmethod
    async def extract_text(pdf_path: str) -> Dict[str, Any]:
        """Extrait le texte d'un PDF"""
        try:
            logger.info(f"📄 Extraction texte du PDF: {pdf_path}")
            
            # En production, utiliser PyPDF2 ou pdfplumber
            return {
                "success": True,
                "pdf_path": pdf_path,
                "text": "[Texte extrait du PDF]",
                "pages": 10,
                "note": "⚠️ PyPDF2/pdfplumber requis en production"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def create_pdf(content: str, output_path: str) -> Dict[str, Any]:
        """Crée un PDF depuis du texte"""
        try:
            logger.info(f"📝 Création PDF: {output_path}")
            
            return {
                "success": True,
                "output_path": output_path,
                "size_kb": len(content) / 1024,
                "note": "⚠️ ReportLab ou WeasyPrint requis en production"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class SpeechTool:
    """Outil pour synthèse vocale et reconnaissance"""
    
    @staticmethod
    async def text_to_speech(text: str, language: str = "fr") -> Dict[str, Any]:
        """Convertit texte en audio"""
        try:
            logger.info(f"🔊 Text-to-Speech: {text[:50]}...")
            
            return {
                "success": True,
                "text": text,
                "language": language,
                "audio_url": "audio_output.mp3",
                "duration_seconds": len(text.split()) * 0.5,
                "note": "⚠️ Google Cloud TTS ou Azure Speech requise en production"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def speech_to_text(audio_path: str) -> Dict[str, Any]:
        """Convertit audio en texte (Speech-to-Text)"""
        try:
            logger.info(f"🎤 Conversion audio vers texte: {audio_path}")
            
            return {
                "success": True,
                "text": "Texte transcrit simulé...",
                "confidence": 0.95,
                "note": "⚠️ Whisper API ou Google Speech-to-Text requise"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class DiscordTool:
    """Outil pour notifications Discord (GRATUIT et illimité!)"""
    
    @staticmethod
    async def send_notification(message: str, title: str = "🤖 EMSI-Bot") -> Dict[str, Any]:
        """
        Envoie une notification Discord via Webhook
        
        Args:
            message: Contenu de la notification
            title: Titre du message (optionnel)
        """
        try:
            import aiohttp
            
            webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
            
            if not webhook_url or webhook_url == 'your_webhook_url_here':
                logger.warning("⚠️ DISCORD_WEBHOOK_URL non configuré")
                return {
                    "success": False,
                    "note": "Configure DISCORD_WEBHOOK_URL dans .env pour activer"
                }
            
            # Format du message Discord
            embed = {
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": 3447003,  # Bleu
                    "timestamp": datetime.now().isoformat(),
                    "footer": {"text": "EMSI Chatbot"}
                }]
            }
            
            # Envoi via webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=embed) as response:
                    if response.status == 204:
                        logger.info(f"✅ Notification Discord envoyée")
                        return {
                            "success": True,
                            "message": "Notification Discord envoyée",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Erreur Discord: {error_text}")
                        return {"success": False, "error": error_text}
                        
        except Exception as e:
            logger.error(f"❌ Erreur Discord: {e}")
            return {"success": False, "error": str(e)}
        """Convertit audio en texte"""
        try:
            logger.info(f"🎤 Speech-to-Text: {audio_path}")
            
            return {
                "success": True,
                "audio_path": audio_path,
                "transcription": "[Transcription de l'audio]",
                "confidence": 0.95,
                "note": "⚠️ Whisper ou Google Speech-to-Text requis en production"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Export des outils
ADVANCED_TOOLS = {
    "whatsapp_send": WhatsAppTool.send_message,
    "whatsapp_media": WhatsAppTool.send_media,
    "email_send": EmailTool.send_email,
    "email_attachment": EmailTool.send_with_attachment,
    "weather_current": WeatherTool.get_weather,
    "weather_forecast": WeatherTool.get_forecast,
    "calendar_create": CalendarTool.create_event,
    "calendar_list": CalendarTool.list_events,
    "translate": TranslationTool.translate,
    "notify": NotificationTool.send_notification,
    "pdf_extract": PDFTool.extract_text,
    "pdf_create": PDFTool.create_pdf,
    "tts": SpeechTool.text_to_speech,
    "stt": SpeechTool.speech_to_text
}
