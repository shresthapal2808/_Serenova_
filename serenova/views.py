
import os

from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import JournalEntry, SoundscapeMix
import requests
from django.http import JsonResponse
import json
from groq import Groq
from .models import Post, Comment, Reaction 
from django.shortcuts import get_object_or_404
from .forms import CustomUserRegisterForm
from .models import Profile
from django.contrib import messages
from django.utils import timezone


def home(request):
    return render(request,'serenova/home.html')

#New users
def register_view(request):
    form = CustomUserRegisterForm()

    if request.method == 'POST':
        form = CustomUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Save extra fields
            Profile.objects.create(
                user=user,
                country=form.cleaned_data['country'],
                phone=form.cleaned_data['phone']
            )

            login(request, user)
            return redirect('home')
        else:
            print(form.errors)

    return render(request, 'serenova/register.html', {'form': form})


#Existing users
def login_view(request):
    form = AuthenticationForm()

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')

    return render(request, 'serenova/login.html', {'form': form})



#logout view
def logout_view(request):
    logout(request)
    return redirect('home')


#All Features view

@login_required(login_url='/login/')
def community_view(request):
    return render(request, 'serenova/community.html')


def quotes_view(request):
    return render(request, 'serenova/quotes.html')

# @login_required(login_url='/login/')
# def soundscape(request):
#     mixes = SoundscapeMix.objects.filter(user=request.user)
#     return render(request, "serenova/soundscape.html", {"mixes": mixes})

def soundscape(request):
    if request.user.is_authenticated:
        mixes = SoundscapeMix.objects.filter(user=request.user)
    else:
        mixes = []  # no mixes for guest

    return render(request, "serenova/soundscape.html", {"mixes": mixes})


#APIS
# #soundscaping
# @login_required(login_url='/login/')
# def save_mix(request):
#     if request.method == "POST":
#         data = json.loads(request.body)

#         SoundscapeMix.objects.create(
#             user=request.user,
#             name=data["name"],
#             sounds=json.dumps(data["sounds"])
#         )

#         return JsonResponse({"status": "ok"})

def save_mix(request):
    if request.method == "POST":

        # 🔒 check login manually
        if not request.user.is_authenticated:
            return JsonResponse({
                "status": "error",
                "message": "login required"
            }, status=401)

        data = json.loads(request.body)

        SoundscapeMix.objects.create(
            user=request.user,
            name=data["name"],
            sounds=json.dumps(data["sounds"])
        )

        return JsonResponse({"status": "ok"})


#Handling next page after login
# def login_view(request):
#     next_url = request.GET.get('next', '/')

#     if request.method == "POST":
#         # login logic...

#         return redirect(next_url)

#     return render(request, "serenova/login.html")

FREESOUND_API_KEY = os.getenv("FREESOUND_API_KEY")

def search_sounds(request):
    query = request.GET.get("q")

    url = "https://freesound.org/apiv2/search/text/"
    params = {
        "query": query,
        "token": FREESOUND_API_KEY,
        "fields": "name,previews",
        "filter": "duration:[1 TO 30]"
    }

    res = requests.get(url, params=params)
    data = res.json()

    results = []
    for sound in data.get("results", []):
        if "previews" in sound:
            results.append({
                "name": sound["name"],
                "preview": sound["previews"]["preview-hq-mp3"]
            })

    return JsonResponse({"results": results})


#QUOTES + MOOD TRACKING VIEWS

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MOOD_PROMPTS = {
    "happy":    "You are a warm life coach. Give one short uplifting quote (2-3 sentences max) for someone feeling happy. No preamble, just the quote.",
    "sad":      "You are a compassionate therapist. Give one short comforting quote (2-3 sentences max) for someone feeling sad. No preamble, just the quote.",
    "anxious":  "You are a calming meditation guide. Give one short calming quote (2-3 sentences max) for someone feeling anxious. No preamble, just the quote.",
    "tired":    "You are a gentle coach. Give one short motivational quote (2-3 sentences max) for someone feeling tired. No preamble, just the quote.",
    "stressed": "You are a mindfulness expert. Give one short peaceful quote (2-3 sentences max) for someone feeling stressed. No preamble, just the quote.",
}

def get_quote(request):
    mood = request.GET.get("mood", "happy")
    system_prompt = MOOD_PROMPTS.get(mood, MOOD_PROMPTS["happy"])

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # model name
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Give me a quote."}
            ],
            max_tokens=120,
            temperature=0.9,
        )
        quote = response.choices[0].message.content.strip()
        return JsonResponse({"content": quote})

    except Exception as e:
        print("Groq ERROR:", str(e))
        return JsonResponse({
             "content": str(e),
            "author": "Serenova"
        })


#Community without API

def community_view(request):

    # 🔒 BLOCK ACTIONS IF NOT LOGGED IN
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("/login/")

        form_type = request.POST.get("form_type")

        # 📝 POST
        if form_type == "post":
            content = request.POST.get("content")
            if content:
                Post.objects.create(user=request.user, content=content)

        # 💬 COMMENT
        elif form_type == "comment":
            text = request.POST.get("comment_text")
            post_id = request.POST.get("post_id")

            if text:
                Comment.objects.create(
                    user=request.user,
                    post_id=post_id,
                    text=text
                )

        return redirect("community")

    # 📦 FETCH POSTS
    posts = Post.objects.select_related('user')\
        .prefetch_related('comments', 'reactions')\
        .order_by('-created_at')

    # ❤️ ADD REACTION COUNTS
    for post in posts:
        reactions = post.reactions.all()

        post.support_count = reactions.filter(reaction_type='support').count()
        post.relate_count = reactions.filter(reaction_type='relate').count()
        post.calm_count = reactions.filter(reaction_type='calm').count()
        post.strength_count = reactions.filter(reaction_type='strength').count()
        post.appreciate_count = reactions.filter(reaction_type='appreciate').count()

    return render(request, "serenova/community.html", {"posts": posts})


# ❤️ REACTION TOGGLE
@login_required(login_url='/login/')
def react_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    reaction_type = request.POST.get("reaction_type")

    existing = Reaction.objects.filter(user=request.user, post=post).first()

    if existing:
        if existing.reaction_type == reaction_type:
            existing.delete()
        else:
            existing.reaction_type = reaction_type
            existing.save()
    else:
        Reaction.objects.create(
            user=request.user,
            post=post,
            reaction_type=reaction_type
        )

    return redirect("community")


# 🗑 DELETE POST
@login_required(login_url='/login/')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user == request.user:
        post.delete()

    return redirect("community")


#journaling
# Mood choices surfaced in template
MOODS = ["Calm", "Anxious", "Grateful", "Tired", "Happy", "Sad"]

def journal_view(request):
    """
    GET  → render journal page
           - authenticated: show write + history
           - anonymous:     show guest lock screen

    POST → save a new entry (login required via check below)
    """
    if request.method == "POST":
        # Guard: only authenticated users can POST
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to save entries.")
            return redirect('login')

        content = request.POST.get("content", "").strip()
        mood    = request.POST.get("mood", "").strip()

        if not mood:
            messages.error(request, "Please select a mood before saving ✨")
            entires = JournalEntry.objects.filter(user=request.user).order_by('-created_at')
            return render(request, 'serenova/journal.html', {
                'entries': entires,
                'moods': MOODS,
                'today': timezone.now(),
                'draft': content,  # pre-fill with unsaved content
            })

        if content:
            JournalEntry.objects.create(
                user    = request.user,
                content = content,
                mood    = mood or None,   # store None if no mood chosen
            )
            messages.success(request, "Entry saved safely ✦")
        else:
            messages.warning(request, "Write something before saving.")

        return redirect('journal')

    # GET — fetch past entries for logged-in users
    entries = (
        JournalEntry.objects
        .filter(user=request.user)
        .order_by('-created_at')
        if request.user.is_authenticated
        else JournalEntry.objects.none()
    )

    context = {
        'entries': entries,
        'moods':   MOODS,
        'today':   timezone.now(),
    }
    return render(request, 'serenova/journal.html', context)


@login_required
def journal_edit(request, pk):
    """Load an existing entry back into the textarea for editing."""
    entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        mood    = request.POST.get("mood", "").strip()
        if content:
            entry.content = content
            entry.mood    = mood or entry.mood
            entry.save()
            messages.success(request, "Entry updated ✦")
        return redirect('journal')

    # Pre-fill the textarea with existing content
    entries = JournalEntry.objects.filter(
        user=request.user).order_by('-created_at')
    context = {
        'entries': entries,
        'moods':   MOODS,
        'today':   timezone.now(),
        'draft':   entry.content,   # pre-fills {{ draft }} in template
        'edit_mode': True,
        'entry_id': entry.id,
        'selected_mood': entry.mood,  # to pre-select the mood in the dropdown
    }
    return render(request, 'serenova/journal.html', context)


@login_required
def journal_delete(request, pk):
    """Delete a journal entry (POST only for safety)."""
    entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)
    if request.method == "POST":
        entry.delete()
        messages.success(request, "Entry deleted.")
    return redirect('journal')

def api_community_view(request):
    return render(request, 'serenova/api_community.html')


#ABOUT
def about(request):
    return render(request, 'serenova/about.html')