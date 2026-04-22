from django.utils import timezone  
from django.contrib.auth.models import User
from django.db import models


#user profile for registration and storing additional user information
COUNTRY_CHOICES = [
    ('IN', 'India'),
    ('US', 'United States'),
    ('UK', 'United Kingdom'),
    ('CA', 'Canada'),
    ('AU', 'Australia'),
    ('DE', 'Germany'),
    ('FR', 'France'),
    ('JP', 'Japan'),
    ('CN', 'China'),
    ('BR', 'Brazil'),
    ('IT', 'Italy'),
    ('ES', 'Spain'),
    ('NL', 'Netherlands'),
    ('BE', 'Belgium'),
    ('SG', 'Singapore'),
    ('ZA', 'South Africa'),
    ('RU', 'Russia'),
    ('MX', 'Mexico'),
    ('KR', 'South Korea'),
    ('AE', 'UAE'),
]
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username




#Soundscape Mix model to store user created mixes in the database
class SoundscapeMix(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sounds = models.TextField()   # store preview URLs
    created_at = models.DateTimeField(auto_now_add=True)

#Community
class Post(models.Model):
    MOOD_CHOICES = [
        ("happy", "Happy"),
        ("sad", "Sad"),
        ("anxious", "Anxious"),
        ("motivated", "Motivated"),
        ("calm", "Calm"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, default="calm")  # ✅ ADD THIS
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:30]

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:30]

class Reaction(models.Model):
    REACTION_CHOICES = [
        ('support', '❤️ Support'),
        ('relate', '🤝 Relate'),
        ('calm', '🌿 Calm'),
        ('strength', '💪 Strength'),
        ('appreciate', '🌟 Appreciate'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)

    class Meta:
        unique_together = ('user', 'post')  # one reaction per user per post


#journaling model to store user journal entries in the database
class JournalEntry(models.Model):
    user       = models.ForeignKey(
                    User,
                    on_delete=models.CASCADE,
                    related_name='journal_entries'
                 )
    content    = models.TextField()
    mood       = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # set once on create
    updated_at = models.DateTimeField(auto_now=True)      # updates on save

    class Meta:
        ordering = ['-created_at']   # newest first by default

    def __str__(self):
        return f"{self.user.username} — {self.created_at.strftime('%b %d, %Y')}"