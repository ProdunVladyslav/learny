from django import forms


class CreateFlashcardForm(forms.Form):
    front     = forms.CharField(max_length=200)
    back      = forms.CharField(max_length=200)
    hint      = forms.CharField(max_length=500, required=False)
    deck_id   = forms.IntegerField()
    audio_url = forms.URLField(max_length=200, required=False)
    image_url = forms.URLField(max_length=200, required=False)

class BulkCreateFlashcardsForm(forms.Form):
    raw_string = forms.CharField(required=False) # format: front-back(hint);front-back(hint);front-back (hint);
    deck_id = forms.IntegerField()


class UpdateFlashcardForm(forms.Form):
    front     = forms.CharField(max_length=200, required=False)
    back      = forms.CharField(max_length=200, required=False)
    hint      = forms.CharField(max_length=500, required=False)
    audio_url = forms.URLField(max_length=200, required=False)
    image_url = forms.URLField(max_length=200, required=False)


class CreateDeckForm(forms.Form):
    title             = forms.CharField(max_length=30)
    description       = forms.CharField(max_length=500, required=False)
    language_to_code  = forms.CharField(max_length=10, required=True)
    language_from_code = forms.CharField(max_length=10, required=False)
    is_public         = forms.BooleanField(required=False)


class UpdateDeckForm(forms.Form):
    title       = forms.CharField(max_length=30, required=False)
    description = forms.CharField(max_length=500, required=False)
    is_public   = forms.BooleanField(required=False)

class ListDecksFilterForm(forms.Form):
    ORDER_CHOICES = [
        ('-created_at', 'Newest first'),
        ('created_at',  'Oldest first'),
        ('title',       'Title A–Z'),
        ('-title',      'Title Z–A'),
    ]

    search     = forms.CharField(required=False)
    is_public  = forms.NullBooleanField(required=False)
    language_from = forms.CharField(max_length=10, required=False)
    language_to = forms.CharField(max_length=10, required=False)
    order_by   = forms.ChoiceField(choices=ORDER_CHOICES, required=False)