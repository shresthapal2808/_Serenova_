from django.contrib import admin
from .models import SoundscapeMix
from .models import Profile
from .models import JournalEntry
from .models import Post

admin.site.register(SoundscapeMix)
admin.site.register(Profile)
admin.site.register(JournalEntry)
admin.site.register(Post)