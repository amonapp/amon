from django import forms

from amon.apps.bookmarks.models import bookmarks_model


BOOKMARK_TYPES =[('server','Server'), ('metric','Metric'), ]

class BookMarkForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BookMarkForm, self).__init__(*args, **kwargs)



    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Bookmark Name', 'required': True}))
    type = forms.ChoiceField(required=True, choices=BOOKMARK_TYPES, initial='server')
    tags = forms.CharField(required=True)


    def save(self):
        data = self.cleaned_data
        bookmark_type = data.get('type')

        bookmarks_model.create(data)


        return bookmark_type

    