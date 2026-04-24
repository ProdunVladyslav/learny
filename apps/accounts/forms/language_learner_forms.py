from django import forms


class CreateLanguageLearnerForm(forms.Form):
    language_to_code   = forms.CharField(max_length=10)
    language_from_code = forms.CharField(max_length=10, required=False)


class UpdateLanguageLearnerForm(forms.Form):
    language_from_code = forms.CharField(max_length=10, required=False)
    is_active          = forms.BooleanField(required=False)