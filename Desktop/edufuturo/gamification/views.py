from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def achievements_view(request):
    user = request.user
    achievements = user.achievements.all().select_related('badge', 'course')
    xp_profile = user.xp_profile if hasattr(user, 'xp_profile') else None
    all_badges = Badge.objects.all()

    return render(request, 'gamification/achievements.html', {
        'achievements': achievements,
        'xp_profile': xp_profile,
        'all_badges': all_badges,
    })