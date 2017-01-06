from amon.apps.core.views import *

from amon.apps.bookmarks.models import bookmarks_model
from amon.apps.bookmarks.forms import BookMarkForm

@login_required
def add(request):

    form_type = 'servers'

    if request.method == 'POST':

        form = BookMarkForm(request.POST)


        if form.is_valid():
            form_type = form.save()
            messages.add_message(request, messages.INFO, 'Bookmark created')
        else:
            messages.add_message(request, messages.INFO, form.errors)


        if form_type == 'server':
            url = reverse('servers')
        else:
            url = reverse('metrics')

        return redirect(url)

    else:
        return redirect(reverse('servers'))


@login_required
def delete(request, bookmark_id=None):
    bookmark = bookmarks_model.get_by_id(bookmark_id)
    bookmark_type = bookmark.get('type')

    bookmarks_model.delete(bookmark_id)

    if bookmark_type == 'server':
        url = reverse('servers')
    else:
        url = reverse('metrics')
    

    messages.add_message(request, messages.INFO, 'Bookmark deleted')

    return redirect(url)