# -*- coding: utf-8 -*-

from models import SuppliedAnimal, SuppliedConsumable, AnimalGroup
from django import forms


def get_input_date_format():
    return "%d/%m/%Y"


class SupplyForm(forms.Form):
    """
        Основа для формы поставки
    """
    date = forms.DateField(
        widget=forms.DateInput(),
        label=u"Дата поступления",
        input_formats=[get_input_date_format()]
    )

    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 3,
        }),
        label=u"Комментарий"
    )


class AddAnimalForm(forms.ModelForm):
    """
        Используется для генерации полей параметров добавленных в поставку животных
    """
    class Meta:
        model = SuppliedAnimal
        exclude = ("supply",)

    def __init__(self):
        super(AddAnimalForm, self).__init__()
        self.fields['animal_type'].widget.attrs.update({"data-role": "fieldset-name-source"})


class AddConsumableForm(forms.ModelForm):
    """
        Используется для генерации полей параметров добавленных в поставку потребностей
    """
    class Meta:
        model = SuppliedConsumable
        exclude = ("supply",)

    def __init__(self):
        super(AddConsumableForm, self).__init__()
        self.fields['consumable_type'].widget.attrs.update({"data-role": "fieldset-name-source"})


class ReportForm(forms.Form):
    """
        Форма для запроса отчёта
    """
    group = forms.ChoiceField(
        choices=AnimalGroup.objects.all().values_list("id", "name"),
        label=u"Группа"
    )

    date_to = forms.DateField(
        widget=forms.DateInput(),
        label=u"Рассчитать до",
        input_formats=[get_input_date_format()]
    )

    spawn = forms.BooleanField(
        label=u"Учитывать размножение",
        initial=False,
        required=False
    )