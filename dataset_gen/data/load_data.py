import os
import sys
import csv
import django
from django.conf import settings
from time import sleep

###########################################
sys.path.append("../")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dataset_gen.settings')
django.setup()
from data.models import Phrase, Ner, Valid

def add_value(text, has_parent, id_prev, id_db):
    phrases = Phrase.objects.filter(id_db=id_db).filter(text=text)
    if phrases.count() == 0:
        phrase = Phrase()
        phrase.text = text
        phrase.has_parent = True if has_parent=='1' else False
        phrase.id_prev = id_prev if has_parent=='1' else ''
        phrase.id_db = id_db
        phrase.save()
        
        id_cur = str(phrase.pk)
        return id_cur
    return ''

def add_entitie(name, desc, abbr, color, order):
    if Ner.objects.filter(abbr=abbr).count() == 0:
        newNer = Ner()
        newNer.name = name
        newNer.description = desc
        newNer.abbr = abbr
        newNer.color = color
        newNer.order = order
        newNer.save()

def main():
    print('Start add phrase to DB')
    filedata = './phrase_data.csv'
    with open(filedata, 'r') as f:
        fdata = csv.reader(f)

        prev_phrase_id = ''
        counter = 0
        for row in fdata:
            if fdata.line_num > 1:
                prev_phrase_id = add_value(text=row[1],
                                           has_parent=row[2],
                                           id_prev=str(prev_phrase_id),
                                           id_db=row[4])
                print(prev_phrase_id)
    print('End add phrase to DB')
    print()
    
    print('Start add entities to DB')
    with open('./entities.csv', 'r') as f:
        fdata = csv.reader(f)
        for row in fdata:
            if fdata.line_num > 1:
                add_entitie(name=row[0],
                            desc=row[1],
                            abbr=row[2],
                            color=row[3],
                            order=row[4])
    print('End add phrase to DB')
    print()

    print('Start add valid to DB')
    Valid(name='Валидно', value='True').save()
    Valid(name='Не валидно', value='False').save()
    print('End add valid to DB')

    print('Finita')

if __name__ == '__main__':
    main()