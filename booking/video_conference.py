"""
Video consultation module for Hills Clinic.

Provides functionality for:
- Scheduling video consultations
- Generating meeting rooms (Jitsi Meet)
- Managing video call sessions
"""
import uuid
import hashlib
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone


class VideoConferenceService:
    """Service class for managing video consultations."""
    
    # Using Jitsi Meet (free, no API key required for basic usage)
    JITSI_DOMAIN = "meet.jit.si"
    
    @classmethod
    def generate_room_id(cls, consultation_id: int, patient_email: str) -> str:
        """
        Generate a unique, secure room ID for the consultation.
        
        Args:
            consultation_id: The consultation record ID
            patient_email: Patient's email for hashing
        
        Returns:
            Unique room identifier
        """
        # Create a hash-based room ID for privacy
        unique_string = f"{consultation_id}-{patient_email}-{uuid.uuid4()}"
        hash_object = hashlib.sha256(unique_string.encode())
        room_hash = hash_object.hexdigest()[:12]
        
        return f"HillsClinic-{room_hash}"
    
    @classmethod
    def get_meeting_url(cls, room_id: str) -> str:
        """
        Get the full meeting URL for a room.
        
        Args:
            room_id: The room identifier
        
        Returns:
            Full Jitsi Meet URL
        """
        return f"https://{cls.JITSI_DOMAIN}/{room_id}"
    
    @classmethod
    def get_meeting_config(cls, room_id: str, display_name: str, is_moderator: bool = False) -> dict:
        """
        Get Jitsi Meet configuration for embedding.
        
        Args:
            room_id: The room identifier
            display_name: Name to display in meeting
            is_moderator: Whether user is the meeting host
        
        Returns:
            Configuration dictionary for Jitsi API
        """
        return {
            'roomName': room_id,
            'width': '100%',
            'height': 600,
            'parentNode': 'meet',
            'configOverwrite': {
                'startWithAudioMuted': True,
                'startWithVideoMuted': False,
                'enableClosePage': True,
                'disableDeepLinking': True,
                'prejoinPageEnabled': False,
                'enableWelcomePage': False,
            },
            'interfaceConfigOverwrite': {
                'TOOLBAR_BUTTONS': [
                    'microphone', 'camera', 'desktop', 'fullscreen',
                    'fodeviceselection', 'hangup', 'chat', 'settings',
                    'videoquality', 'filmstrip', 'tileview',
                ],
                'SHOW_JITSI_WATERMARK': False,
                'SHOW_WATERMARK_FOR_GUESTS': False,
                'DEFAULT_BACKGROUND': '#1a1a2e',
                'TOOLBAR_ALWAYS_VISIBLE': True,
            },
            'userInfo': {
                'displayName': display_name,
            }
        }
    
    @classmethod
    def create_consultation_room(cls, consultation) -> tuple:
        """
        Create a video consultation room.
        
        Args:
            consultation: VideoConsultation model instance
        
        Returns:
            Tuple of (room_id, meeting_url)
        """
        room_id = cls.generate_room_id(
            consultation.id,
            consultation.patient.email
        )
        meeting_url = cls.get_meeting_url(room_id)
        
        return room_id, meeting_url
    
    @classmethod
    def is_meeting_active(cls, scheduled_time: datetime, duration_minutes: int = 60) -> bool:
        """
        Check if a meeting should be active based on scheduled time.
        
        Args:
            scheduled_time: When the meeting was scheduled
            duration_minutes: Expected meeting duration
        
        Returns:
            True if meeting should be accessible
        """
        now = timezone.now()
        
        # Allow joining 10 minutes early
        start_buffer = timedelta(minutes=10)
        # Allow staying until duration + 15 minutes after
        end_buffer = timedelta(minutes=duration_minutes + 15)
        
        meeting_start = scheduled_time - start_buffer
        meeting_end = scheduled_time + end_buffer
        
        return meeting_start <= now <= meeting_end
    
    @classmethod
    def get_join_instructions(cls) -> dict:
        """Get instructions for joining video consultation."""
        return {
            'requirements': [
                'Modern web browser (Chrome, Firefox, Safari, or Edge)',
                'Stable internet connection (minimum 2 Mbps)',
                'Working webcam and microphone',
                'Quiet, well-lit environment',
            ],
            'tips': [
                'Test your audio and video before the call',
                'Join 5 minutes before your scheduled time',
                'Have your medical documents ready to share',
                'Prepare a list of questions you want to ask',
            ],
            'support': {
                'email': 'support@hillsclinic.com',
                'whatsapp': '+1234567890',
            }
        }
