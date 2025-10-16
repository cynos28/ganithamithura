
import json
import random
import logging
from datetime import datetime
from livekit import api

logger = logging.getLogger(__name__)


class LiveKitService:    
    def __init__(self, url, api_key, api_secret):
        self.url = url
        self.api_key = api_key
        self.api_secret = api_secret
        self.livekit_api = None
        
        if url and api_key and api_secret:
            try:
                self.livekit_api = api.LiveKitAPI(url, api_key, api_secret)
                logger.info("LiveKit API initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize LiveKit API: {e}")
    
    def generate_token(self, room_name=None, participant_name=None, difficulty='easy'):
        """
        Generate LiveKit access token
        
        Args:
            room_name: Name of the room (auto-generated if None)
            participant_name: Name of the participant (auto-generated if None)
            difficulty: Question difficulty level
            
        Returns:
            Dictionary with token and connection details
        """
        try:
            # Generate default names if not provided
            if not room_name:
                room_name = f'math-practice-{int(datetime.now().timestamp())}'
            if not participant_name:
                participant_name = f'student-{random.randint(1000, 9999)}'
            
            # Create token with appropriate grants
            token = api.AccessToken(self.api_key, self.api_secret)
            token.with_identity(participant_name)
            token.with_name(participant_name)
            token.with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            ))
            token.with_metadata(json.dumps({
                'difficulty': difficulty,
                'timestamp': datetime.now().isoformat()
            }))
            
            jwt_token = token.to_jwt()
            
            return {
                'success': True,
                'token': jwt_token,
                'url': self.url,
                'room': room_name,
                'participant': participant_name
            }
            
        except Exception as e:
            logger.error(f"Failed to generate token: {e}")
            return {
                'error': f'Failed to generate token: {str(e)}',
                'success': False
            }
    
    def list_rooms(self):
        """
        List active LiveKit rooms
        
        Returns:
            Dictionary with list of rooms
        """
        try:
            if not self.livekit_api:
                return {
                    'error': 'LiveKit API not initialized',
                    'success': False
                }
            
            rooms = self.livekit_api.room.list_rooms(api.ListRoomsRequest())
            
            room_list = []
            for room in rooms.rooms:
                room_list.append({
                    'name': room.name,
                    'sid': room.sid,
                    'num_participants': room.num_participants,
                    'creation_time': room.creation_time,
                    'metadata': room.metadata
                })
            
            return {
                'success': True,
                'rooms': room_list,
                'count': len(room_list)
            }
            
        except Exception as e:
            logger.error(f"Failed to list rooms: {e}")
            return {
                'error': f'Failed to list rooms: {str(e)}',
                'success': False
            }
    
    def process_webhook(self, webhook_data):
        """
        Process LiveKit webhook events
        
        Args:
            webhook_data: Webhook payload
            
        Returns:
            Dictionary with processing result
        """
        try:
            event_type = webhook_data.get('event')
            
            logger.info(f"Received LiveKit webhook: {event_type}")
            logger.debug(f"Webhook data: {json.dumps(webhook_data, indent=2)}")
            
            # Handle different event types
            handlers = {
                'room_started': self._handle_room_started,
                'room_finished': self._handle_room_finished,
                'participant_joined': self._handle_participant_joined,
                'participant_left': self._handle_participant_left,
            }
            
            handler = handlers.get(event_type)
            if handler:
                handler(webhook_data)
            
            return {
                'success': True,
                'message': 'Webhook received'
            }
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {
                'error': 'Webhook processing failed',
                'success': False
            }
    
    def _handle_room_started(self, data):
        """Handle room started event"""
        room_name = data.get('room', {}).get('name')
        logger.info(f"Room started: {room_name}")
    
    def _handle_room_finished(self, data):
        """Handle room finished event"""
        room_name = data.get('room', {}).get('name')
        logger.info(f"Room finished: {room_name}")
    
    def _handle_participant_joined(self, data):
        """Handle participant joined event"""
        participant_identity = data.get('participant', {}).get('identity')
        logger.info(f"Participant joined: {participant_identity}")
    
    def _handle_participant_left(self, data):
        """Handle participant left event"""
        participant_identity = data.get('participant', {}).get('identity')
        logger.info(f"Participant left: {participant_identity}")