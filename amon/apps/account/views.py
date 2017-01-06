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

    return render_to_response('account/login.html', {
        'form': form,
    },
    context_instance=RequestContext(request))


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

    return render_to_response('account/create_admin_user.html', {
        'form': form,
    },
    context_instance=RequestContext(request))


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


    return render_to_response('account/view_profile.html', {
        "form": form,
    },
    context_instance=RequestContext(request))

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


    return render_to_response('account/reset_password.html', {
        "form": form,
        "token": token
    },
    context_instance=RequestContext(request))

def forgotten_password(request):

    form = ForgottenPasswordForm()

    if request.method == 'POST':
        form = ForgottenPasswordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'A Reset password email was sent to the specified email.')
            return redirect(reverse('forgotten_password'))


    return render_to_response('account/forgotten_password.html', {
        "form": form,
    },
    context_instance=RequestContext(request))

@login_required
def change_password(request):
    form = ChangePasswordForm(user=request.user)

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Password updated.')
            return redirect(reverse('view_profile'))


    return render_to_response('account/change_password.html', {
        "form": form,
    },
    context_instance=RequestContext(request))


@login_required
def ajax_update_preferences(request):
    pass


@login_required
def migrate_four_to_five(request):

    from amon.apps.notifications.models import notifications_model
    from amon.apps.notifications.legacymodels import email_recepient_model
    from amon.apps.notifications.legacymodels import webhooks_model
    from amon.apps.alerts.models import alerts_model

    # Move emails
    all_emails = email_recepient_model.get_all()
    for e in all_emails:
        email_exists = notifications_model.collection.find_one({'email': e.get('email'), 'provider_id': 'email'})
        if email_exists == None:
            notifications_model.save(data={"email": e.get('email')}, provider_id='email')


    # Move webhooks
    all_webhooks = webhooks_model.get_all()
    for e in all_webhooks:
        hook_exists = notifications_model.collection.find_one({'url': e.get('url'), 'provider_id': 'webhook'})
        if hook_exists == None:
            data = {
                'url': e.get('url'),
                'name': e.get('url'),
                'secret': e.get('secret')
            }
            notifications_model.save(data=data, provider_id='webhook')

    # Set default names
    all_notifications = notifications_model.get_all()
    for noti in all_notifications:
        if noti.get('provider_id') not in ['webhook', 'email']:
            name = noti.get('name', None)
            if name == None:
                notifications_model.update(data={'name': 'default'}, id=noti.get('_id'))

    # Update all alerts
    alerts = alerts_model.get_all()
    for alert in alerts:
        new_notifications_list = []
        emails = alert.get('email_recepients', [])
        webhooks = alert.get('webhooks', [])
        old_notifications = alert.get('notifications', [])


        for email in emails:
            email_from_old_model = email_recepient_model.get_by_id(email)
            if email_from_old_model:
                new_email_location = notifications_model.collection.find_one({'email': email_from_old_model.get('email'), 'provider_id': 'email'})

                if new_email_location:
                    _id = "email:{0}".format(new_email_location.get('_id'))
                    new_notifications_list.append(_id)

        for hook in webhooks:
            hook_from_old_model = webhooks_model.get_by_id(hook)
            if hook_from_old_model:
                new_hook_location = notifications_model.collection.find_one({'url': hook_from_old_model.get('url'), 'provider_id': 'webhook'})

                if new_hook_location:
                    _id = "webhook:{0}".format(new_hook_location.get('_id'))
                    new_notifications_list.append(_id)

        for provider in old_notifications:

            new_notification = notifications_model.collection.find_one({'provider_id': provider})
            if new_notification:
                _id = "{0}:{1}".format(provider, new_notification.get('_id'))
                new_notifications_list.append(_id)

        try:
            del alert['email_recepients']
            del alert['webhooks']
        except:
            pass

        alert['notifications'] = new_notifications_list
        alerts_model.update(alert, alert.get('_id'))


    messages.add_message(request, messages.INFO, 'Migration complete.')

    return redirect(reverse('servers'))
