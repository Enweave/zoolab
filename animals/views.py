# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseRedirect

from django.shortcuts import render
from django.template.loader import render_to_string
from animals.forms import SupplyForm, AddAnimalForm, AddConsumableForm, ReportForm, get_input_date_format
from animals.models import Supply, AnimalType, SuppliedAnimal, SuppliedConsumable, ConsumableType
from django.contrib import messages
import datetime
import math


# Генерирует поля формы при добавлении животного в поставку
def get_animals(request):
    if request.is_ajax():
        form = AddAnimalForm()
        item_name = u'Животное'
        html = render_to_string("common/widgets/supplies_fieldset.html", locals())
        return JsonResponse({"html": html})
    return HttpResponseRedirect("/")


# Генерирует поля формы при добавлении потребности в поставку
def get_consumables(request):
    if request.is_ajax():
        form = AddConsumableForm()
        item_name = u'Потребность'
        html = render_to_string("common/widgets/supplies_fieldset.html", locals())
        return JsonResponse({"html": html})
    return HttpResponseRedirect("/")


# генерирует страницу добавления и просмотра поставок
def supplies_page(request):
    # выделенный пункт навигации
    nav_selected = 0
    supplies = Supply.objects.all().order_by("-date")

    form = SupplyForm()
    if request.POST:
        # Основные поля поставки фиксируем с помощью объекта формы
        form = SupplyForm(request.POST)
        if form.is_valid():
            # Животных одинакового пола и типа будем объединять, складывае количество
            # для этого заводим словарь
            grouped_animal_types = {}
            
            # получаем данные животных.
            # в запросе ожидаем увидеть массивы данных по одинаковым ключам : animal_type, animal_gender, animal_count,
            # поскольку все поля в мини-формах для животных являются обязательными, каждый параметр животного
            # будет иметь одинаковый индекс в соответствующем массиве.
            # но вообще это плохая затея ;)
            for i, animal_type in enumerate(request.POST.getlist("animal_type", ())):
                gender = request.POST.getlist("animal_gender")[i]
                count = int(request.POST.getlist("animal_count")[i])
                
                # идентификатор группы
                group_id = "%s%s" % (animal_type, gender)

                # вносим в группу
                current_group = grouped_animal_types.get(group_id, {
                    "type": animal_type,
                    "gender": gender,
                })
                current_group.update({"count": count + current_group.get("count", 0)})

                grouped_animal_types.update({group_id: current_group})

            # c потребностями почти то же самое,
            # только без группировки
            consumables = []
            for i, consumble_type in enumerate(request.POST.getlist("consumable_type", ())):
                consumables.append({"type": consumble_type, "count": int(request.POST.getlist("consumable_count")[i])})

            if grouped_animal_types or consumables:
                # добавляем поставку только в том случае, если есть животные или потребности
                new_supply = Supply(**form.cleaned_data)
                new_supply.save()
                for supplied_animal in grouped_animal_types.values():
                    new_supplied_animal = SuppliedAnimal(
                        supply=new_supply,
                        animal_type=AnimalType.objects.get(id=supplied_animal["type"]),
                        animal_count=supplied_animal["count"],
                        animal_gender=supplied_animal["gender"]
                    )
                    new_supplied_animal.save()
                for consumable in consumables:

                    new_supplied_consumable = SuppliedConsumable(
                        supply=new_supply,
                        consumable_type=ConsumableType.objects.get(id=consumable["type"]),
                        consumable_count=consumable["count"]
                    )
                    new_supplied_consumable.save()
                messages.success(request, u"Успешно добавлена %s" % new_supply)
                
            # после успешной поставки отправляем редирект на страницу поставок, 
            # чтобы исключить случайную повторную отправку формы  
            return HttpResponseRedirect(reverse('animals:supplies'))
    return render(request, "common/supplies.html", locals())

# удаления поставки
def remove_supply(request, pk):
    if request.POST and request.is_ajax():
        supplies = Supply.objects.filter(id=pk)
        if supplies:
            if request.POST.get("confirm"):
                supplies[0].delete()
                return JsonResponse({"success": True})
            return JsonResponse({"success": False})
        else:
            return JsonResponse({"success": False})

    return HttpResponseRedirect("/")

# вспомогательная функция добавления строчки в отчёт
def add_report_row(date, animal_name, count):
    return {
        "date": date,
        "content": "%s x %s" % (animal_name, count)
    }


# Вспомогательный класс
# используется при генерации отчёта
# помещает в себе типы потребностей + количество 
class ConsumablesStorage(object):
    def __init__(self):
        self.items = {}

    # добавить новый тип + количество либо повысить количество уже имеющегося типа
    def update_item(self, iid, count):
        existin = self.items.get(iid)
        if existin:
            self.items.update({iid: existin + count})
        else:
            self.items.update({iid: count})

    # уменьшить количество определённого типа
    # возвращает число - количество потребности, которого не хватает
    def take_item(self, iid, count):
        existin = self.items.get(iid)
        if existin:
            remainin = existin - count
            self.items.update({iid: remainin if remainin > 0 else 0})
            return remainin
        else:
            return -count

# Вспомогательный класс
# используется при генерации отчёта
# помещает в себе типы животных с учётом пола + количество + типы потребностей для каждого типа животного
# учёт пола животного реализуется с помощью дополнительной переменной, которая хранит количество животных женского пола
class AnimalStorage(object):
    def __init__(self):
        self.items = {}

    # добавляем новый тип животного, ессли отсутствует в self.items,
    # если такой тип уже есть - повышаем количество
    def append_item(self, iid, name, count, needs, is_female=False):
        existin = self.items.get(iid)
        if existin:
            existin.update({
                "count": existin.get("count") + count,
            })
            if is_female:
                existin.update({
                    "female_count": existin.get("female_count") + count
                })
        else:
            self.items.update({
                iid: {
                    "name": name,
                    "needs": needs,
                    "count": count,
                    "female_count": count if is_female else 0,
                    "breed_rate": 1, # скорость "рождения" не была оговорена в ТЗ, но мы предусматриваем возможность её поменять
                }
            })

    # убавляет количество животных указанного типа на указанное количество
    # возвращает список элементов, содержащих информацию о погибших животных, которые нужно добавить в отчёт
    def die(self, iid, count, date):
        existin = self.items.get(iid)
        deaths = []
        if existin:
            result_count = existin.get("count") - count
            result_count = result_count if result_count > 0 else 0

            # Животные "умирают" таким образом, чтобы количество разнополых пар было максимальным 
            female_count = existin.get("female_count")
            result_female_count = result_count/2
            existin.update({
                "count": result_count if result_count > 0 else 0,
                "female_count": result_female_count if result_female_count < female_count else female_count
            })
            deaths.append(add_report_row(date, existin.get("name"), count))
        return deaths

    # добавляет количество родившихся животных
    # возвращает эелементы для отчёта
    def breed(self, date=None):
        new_ones = []
        for item in self.items.values():
            pairs = min([item.get("count") - item.get("female_count"), item.get("female_count")])
            new_breed = int(math.floor(pairs*item.get("breed_rate")))
            item.update({
                "count": item.get("count") + new_breed,
                "female_count": item.get("female_count") + new_breed/2
            })
            if new_breed > 0:
                new_ones.append(add_report_row(date, item.get("name"), new_breed))
        return new_ones

# Генерирует с формой для запроса отчёта и,собственно, сам отчёт, если форма отправлена
def reports_page(request):
    DATEFORMAT = get_input_date_format()
    nav_selected = 1
    report_form = ReportForm()

    # "разделы" отчёта
    recommendations = []
    deaths = []
    spawns = []

    if request.POST:
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            # используется в шаблоне, чтобы определить, показывать сообщение или отчёт
            has_report = True
            
            # извлекаем ключ из модели животного в поставке ключ, которые определяет женский пол
            gender_female = SuppliedAnimal.GENDERS[1][0]

            # извлекаем данные из формы
            date_to = report_form.cleaned_data.get("date_to")
            selected_animal_group_id = report_form.cleaned_data.get("group")
            spawn = report_form.cleaned_data.get("spawn") # флаг "учитывать размножение"
            
            # извлекаем из БД поставки до и включая указанную дату
            supplies = list(Supply.objects.filter(date__lte=date_to).order_by("date"))
            if supplies:
                # если есть поставки - инициализируем вспомогательные классы
                animals = AnimalStorage()
                consumables = ConsumablesStorage()

                # симулирует процессы в группе животных втечение указанного количества дней
                # образно говоря, каждый день протекает в 3 этапа:
                #   1) внесение животных и потребностей
                #   2) потребление потребностей и гибель животных в случае дефицита
                #   3) размножение
                # функция определена здесь умышленно, чтобы бы доступ к вспомогательным классам
                def process_phase(supply, span):
                    # первым этапом добавляем животных из указанной поставки...
                    for a in SuppliedAnimal.objects.filter(supply=supply, animal_type__id=selected_animal_group_id):
                        animals.append_item(
                            a.animal_type.id,
                            a.animal_type.name,
                            a.animal_count,
                            a.animal_type.get_needs(),
                            a.animal_gender == gender_female
                        )
                    # ...и потребности
                    for s in SuppliedConsumable.objects.filter(supply=supply):
                        consumables.update_item(s.consumable_type.id, s.consumable_count)

                    # если количество дней 0, дальше ничего не делаем,
                    # это сделано потому, что в один день может быть произведено несколько поставок
                    # и перед произведением расчётов необходимо добавить во вспомогательные классы всё поступившее
                    if span > 0:
                        # симулируем дни
                        for v in range(0, span):
                            # высчитываем дату для отчёта элемента отчёта
                            report_entry_date = (supply.date + datetime.timedelta(days=v)).strftime(DATEFORMAT)
                            
                            # второй этап - симулируем потребление потребностей
                            
                            # однако, есть небольшой изьян - потребности распределяются между типами животных неравномерно
                            for aiid, animal in animals.items.iteritems():
                                # количество потребности, которой не хватило больше всего
                                lowest_efficiency = 0
                                
                                # тип потребности, которой не хватило больше всего
                                highest_need = None
                                
                                current_animal_count = animal.get("count")
                                
                                # проходим по всем типам потребностей для текущего типа животного
                                for need in animal.get("needs"):
                                    if current_animal_count > 0:
                                        # убавляем количство имеющихся потребностей попутно выясняя, сколько остаётся
                                        efficiency = consumables.take_item(
                                            need.consumable_type.id,
                                            need.consumable_per_day * current_animal_count
                                        )
                                        
                                        # отмечаем остаток, чтобы впоследствие выяснить, какой потребности не хватает больше всего
                                        if efficiency < lowest_efficiency:
                                            lowest_efficiency = efficiency
                                            highest_need = need
                                            
                                        # если имеется дефицит в какой потребности - создаём элемент отчёта
                                        if efficiency < 0:
                                            recommendations.append(add_report_row(
                                                report_entry_date,
                                                need.consumable_type.name,
                                                -efficiency,
                                            ))
                                            
                                # используя максимальный дефицит, подсчитываем, сколько животных погибнет
                                if lowest_efficiency < 0:
                                    dead_count = -int(math.ceil(float(lowest_efficiency) * highest_need.consumable_per_day))
                                    new_deaths = animals.die(aiid, dead_count, report_entry_date)
                                    # создаём элементы отчёта с информацией о погибших животных
                                    for d in new_deaths:
                                        deaths.append(d)
                                        
                            # 3-й этап - симулируем размножение животных
                            if spawn:
                                new_spawns = animals.breed(report_entry_date)
                                # создаём элементы отчёта с информацией о "родившихся" животных
                                for n in new_spawns:
                                    spawns.append(n)

                # непосредственно, начало обработки отчёта
                
                # запускаем цикл по всем поставкам, кроме последней
                for i, c_supply in enumerate(supplies[:-1]):
                    # выясняем количество дней между текущей и последующей поставками
                    c_span = (supplies[i+1].date - c_supply.date).days
                    # обрабатыываем полученный промежуток
                    process_phase(c_supply, c_span)
                
                # обрабатываем последнюю (или единственнуую) поставку
                last_span = (date_to - supplies[-1].date).days
                last_supply = supplies[-1]
                process_phase(last_supply, last_span)
                
    return render(request, "common/reports.html", locals())
