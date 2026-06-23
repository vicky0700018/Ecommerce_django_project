from .models import Announcement

def announcements(request):
    active_announcement = Announcement.objects.filter(is_active=True).first()
    return {
        'active_announcement': active_announcement
    }
