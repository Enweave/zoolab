# -*- coding: utf-8 -*-

from models import Supply, SuppliedAnimal, SuppliedConsumable, AnimalGroup
from django import forms


class SupplyForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(),
        label=u"Дата поступления",
        input_formats=["%d/%m/%Y"]
    )

    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 3,
        }),
        label=u"Комментарий"
    )


class AddAnimalForm(forms.ModelForm):
    class Meta:
        model = SuppliedAnimal
        exclude = ("supply",)

    def __init__(self):
        super(AddAnimalForm, self).__init__()
        self.fields['animal_type'].widget.attrs.update({"data-role": "fieldset-name-source"})


class AddConsumableForm(forms.ModelForm):
    class Meta:
        model = SuppliedConsumable
        exclude = ("supply",)

    def __init__(self):
        super(AddConsumableForm, self).__init__()
        self.fields['consumable_type'].widget.attrs.update({"data-role": "fieldset-name-source"})


class ReportForm(forms.Form):
    group = forms.ChoiceField(
        choices=AnimalGroup.objects.all().values_list("id", "name"),
        label=u"Группа"
    )

    date_to = forms.DateField(
        widget=forms.DateInput(),
        label=u"До",
        input_formats=["%d/%m/%Y"]
    )