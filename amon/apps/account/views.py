from amon.apps.core.views import *

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth import get_user_model

from amon.apps.account.models import forgotten_pass_tokens_model
from amon.apps.account.forms import LoginForm
from amon.apps.account.forms import (
    AdminUserForm,
    ChangePasswordForm,
    ForgottenPasswordForm,
    ProfileForm,
    ResetPasswordForm
)

User = get_user_model()


def loginview(request):

    all_users = User.objects.all().count()

    if all_users == 0:
        return redirect(reverse('create_admin_user'))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data['email'], password=data['password'])

            if user:
                login(request, user)
                redirect_url = reverse('servers')

                return redirect(redirect_url)
    else:
        form = LoginForm()

    return render(request, 'account/login.html', {
        'form': form,
    })


def create_admin_user(request):

    all_users = User.objects.all().count()
    if all_users > 0:
        return redirect(reverse('login'))

    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            form.save()

            messages.add_message(request, messages.INFO, 'User created')
            redirect_url = reverse('login')

            return redirect(redirect_url)
    else:
        form = AdminUserForm()

    return render(request, 'account/create_admin_user.html', {
        'form': form,
    })


@login_required
def logout_user(request):
    try:
        del request.account_id
    except:
        pass

    logout(request)
    return redirect(reverse('login'))


@login_required
def view_profile(request):
    form = ProfileForm(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Profile settings updated')


            return redirect(reverse('view_profile'))


    return render(request, 'account/view_profile.html', {
        "form": form,
    })


def reset_password(request, token=None):

    token_object = forgotten_pass_tokens_model.get_one({'token': token})

    if len(token_object) == 0:
        raise Http404

    try:
        user = User.objects.get(email=token_object['email'])
    except:
        user = None
        raise Http404
    

    form = ResetPasswordForm()

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            form.save(user=user)
            messages.add_message(request, messages.INFO, 'Your password has been changed.')
            return redirect(reverse('login'))


    return render(request, 'account/reset_password.html', {
        "form": form,
        "token": token
    })


def forgotten_password(request):
    form = ForgottenPasswordForm()

    if request.method == 'POST':
        form = ForgottenPasswordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'A Reset password email was sent to the specified email.')
            return redirect(reverse('forgotten_password'))


    return render(request, 'account/forgotten_password.html', {
        "form": form,
    })


@login_required
def change_password(request):
    form = ChangePasswordForm(user=request.user)

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Password updated.')
            return redirect(reverse('view_profile'))


    return render(request, 'account/change_password.html', {
        "form": form,
    })