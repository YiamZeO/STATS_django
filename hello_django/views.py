from django.http import JsonResponse
from django import forms


class MyForm(forms.Form):
    name = forms.CharField()
    age = forms.IntegerField()
    gender = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        gender = cleaned_data.get('gender', '')
        if gender is '':
            cleaned_data['gender'] = 'Not have gender'


def hi(request):
    form = MyForm(request.GET)
    if form.is_valid():
        data = {
            'name': form.cleaned_data['name'],
            'age': form.cleaned_data['age'],
            'gender': form.cleaned_data['gender'],
            'access': form.cleaned_data['age'] >= 18
        }
        return JsonResponse(data)
    else:
        return JsonResponse(form.errors, status=400)
