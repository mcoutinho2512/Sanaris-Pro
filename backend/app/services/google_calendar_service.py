"""
Serviço de integração com Google Calendar
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging
from app.core.google_oauth import get_calendar_service

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """Serviço para gerenciar eventos no Google Calendar"""
    
    @staticmethod
    def create_event(
        access_token: str,
        summary: str,
        description: str,
        start_datetime: datetime,
        end_datetime: datetime,
        attendee_email: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict:
        """Criar evento no Google Calendar"""
        try:
            service = get_calendar_service(access_token)
            
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            
            if location:
                event['location'] = location
            
            if attendee_email:
                event['attendees'] = [{'email': attendee_email}]
            
            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"📅 Evento criado: {created_event.get('id')}")
            
            return {
                'success': True,
                'event_id': created_event.get('id'),
                'html_link': created_event.get('htmlLink'),
                'message': 'Evento criado com sucesso!'
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar evento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def update_event(
        access_token: str,
        event_id: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None
    ) -> Dict:
        """Atualizar evento existente"""
        try:
            service = get_calendar_service(access_token)
            
            event = service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            if summary:
                event['summary'] = summary
            if description:
                event['description'] = description
            if start_datetime:
                event['start']['dateTime'] = start_datetime.isoformat()
            if end_datetime:
                event['end']['dateTime'] = end_datetime.isoformat()
            
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"📅 Evento atualizado: {event_id}")
            
            return {
                'success': True,
                'event_id': updated_event.get('id'),
                'message': 'Evento atualizado com sucesso!'
            }
            
        except Exception as e:
            logger.error(f"Erro ao atualizar evento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def delete_event(access_token: str, event_id: str) -> Dict:
        """Deletar evento do calendário"""
        try:
            service = get_calendar_service(access_token)
            
            service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"📅 Evento deletado: {event_id}")
            
            return {
                'success': True,
                'message': 'Evento deletado com sucesso!'
            }
            
        except Exception as e:
            logger.error(f"Erro ao deletar evento: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def list_events(
        access_token: str,
        max_results: int = 10,
        time_min: Optional[datetime] = None
    ) -> Dict:
        """Listar eventos do calendário"""
        try:
            service = get_calendar_service(access_token)
            
            if not time_min:
                time_min = datetime.utcnow()
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return {
                'success': True,
                'events': events,
                'count': len(events)
            }
            
        except Exception as e:
            logger.error(f"Erro ao listar eventos: {e}")
            return {
                'success': False,
                'error': str(e)
            }
