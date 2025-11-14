from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('video_list')
    else:
        form = AuthenticationForm()
    template = 'downloader/login_content.html' if request.htmx else 'downloader/login.html'
    return render(request, template, {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
