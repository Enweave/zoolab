# -*- coding: utf-8 -*-

from models import Supply, SuppliedAnimal, SuppliedConsumable
from django import forms


class SupplyForm(forms.Form):
    BASE_ATTRS = {"class": "form-control"}
    date = forms.DateField(widget=forms.DateInput(), label=u"Дата поступления",input_formats=["%d/%m/%Y"])
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 3,
        }),
        label=u"Комментарий"
    )

    # animals = forms.CharField(widget=forms.HiddenInput())
    # consumables = forms.CharField(widget=forms.HiddenInput())


class AddAnimalForm(forms.ModelForm):
    class Meta:
        model = SuppliedAnimal
        exclude = ("supply",)


class AddConsumableForm(forms.ModelForm):
    class Meta:
        model = SuppliedConsumable
        exclude = ("supply",)