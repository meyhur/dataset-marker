import os
import sys
import json
import requests
from django.utils import timezone
import django
from django.conf import settings
from django.http import JsonResponse
from datetime import timedelta

###########################################
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)  # path to the parent dir of DjangoTastypie
# sys.path.append("/var/www/html/parsersites/")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dataset_gen.settings')
django.setup()
from data.models import Phrase, Skill, Valid, Ner

def markDuringFalse():
    phrases = Phrase.objects.filter(during=True, during_start__lte=(timezone.now()-timedelta(minutes=5)))
    phrases.update(during=False)

def get_full_text(cur_id):
    cur = Phrase.objects.get(pk=cur_id)
    if cur.has_parent:
        has_parent = True
        while has_parent != False:
            cur = getPrev(int(cur.id_prev))
            has_parent = cur.has_parent

    full_text = cur.text
    next_phrase = True
    while next_phrase:
        cur, has_parent = getNext(str(cur.id))
        next_phrase = True if has_parent else False
        if cur:
            full_text = '{}\n{}'.format(full_text, cur.text)

    return full_text.strip()

def getPrev(id_prev):
    return Phrase.objects.get(pk=id_prev)

def getNext(id_prev):
    nex = Phrase.objects.filter(id_prev=id_prev)
    if nex.count() > 0:
        return nex[0], nex[0].has_parent
    return None, False

def updateNers(phrase_id):
    try:
        phrase = Phrase.objects.get(pk=phrase_id)
        r = requests.post('http://192.168.0.88:5000/ner', json={"context": [phrase.text]})
        phrase.ners = r.json()[0]
        phrase.save()
        return phrase.ners
    except Exception as e:
        print(e)
        return ''

def getNersToken(phrase_id):
    phrase = Phrase.objects.get(pk=phrase_id)
    if phrase.ners == '':
        ners = updateNers(phrase_id)
    else:
        ners = json.loads(phrase.ners.replace('\'', '\"'))

    return ners

def getPhrase(element=None):
    # фразы у которых отметка during=True
    # и у которых время вышло
    # ставим метку during=False
    markDuringFalse()

    now = timezone.now()
    obj = {}

    all_phrases = Phrase.objects.all().order_by('-id')
    last_phrase = all_phrases[0]

    if element:
        phrases = Phrase.objects.filter(pk=element)
    else:
        phrases = Phrase.objects.filter(processed=False, during=False).order_by('id')

    if phrases.count() > 0:
        phrase = phrases[0]
        phrase.during = True
        phrase.during_start = now
        phrase.save()

        obj['id'] = phrase.id
        obj['text'] = phrase.text
        obj['full_text'] = get_full_text(phrase.id)
        obj['skills'] = list(phrase.skills.values())
        obj['last_phrase'] = last_phrase.id
        obj['valid'] = phrase.valid.value if phrase.valid else None
        obj['ners'] = getNersToken(phrase.id)

    return obj

def PrevPhrase(element):
    prev_no = True
    while prev_no:
        phrases = Phrase.objects.filter(pk=element-1)
        element -= 1
        if phrases.count() > 0:
            prev_no = False
            return getPhrase(phrases[0].id)

def NextPhrase(element):
    all_phrases = Phrase.objects.all().order_by('-id')
    last_phrase = all_phrases[0]
    
    next_no = True
    while next_no and element < last_phrase.id:
        phrases = Phrase.objects.filter(pk=element+1)
        element += 1
        if phrases.count() > 0:
            next_no = False
            return getPhrase(phrases[0].id)

def getListSkills():
    skills = Skill.objects.all()

    list_obj = []
    for skill in skills:
        obj = {}
        obj['id'] = skill.id
        obj['name'] = skill.name
        obj['desc'] = skill.description
        obj['count'] = Phrase.objects.filter(skills=skill.id).count()
        list_obj.append(obj)

    return list_obj

def addSkill(data):
    newSkill = Skill()
    newSkill.name = data['name']
    newSkill.description = data['desc']
    newSkill.save()

    return getListSkills()

def phraseUpdate(phrase_id, valid, skills, ners):
    objPhrase = Phrase.objects.get(pk=phrase_id)
    objPhrase.processed = True
    objPhrase.valid = Valid.objects.get(value=valid)
    objPhrase.skills.set(skills)
    objPhrase.ners = ners
    objPhrase.save()

def getNers():
    ners = Ner.objects.all()

    list_obj = []
    for ner in ners:
        obj = {}
        obj['id'] = ner.id
        obj['name'] = ner.name
        obj['desc'] = ner.description
        obj['abbr'] = ner.abbr
        obj['color'] = ner.color
        obj['order'] = ner.order
        list_obj.append(obj)
    
    return list_obj

def addNer(ner):
    newNer = Ner()
    newNer.name = ner['name']
    newNer.description = ner['desc']
    newNer.abbr = ner['abbr']
    newNer.color = ner['color']
    newNer.order = ner['sort']
    newNer.save()

def action(request):
    if request.method == "GET":
        data = request.GET
        # print('GET', data)
    elif request.method == "POST":
        data = request.POST
        data = json.loads(list(data.keys())[0])
        # print('POST', data)
    action = data.get('action')
    result = {}

    if action == 'getPhrase':
        result['phrase'] = getPhrase()
    elif action == 'getListSkills':
        result['ListSkills'] = getListSkills()
    elif action == 'addSkill':
        dataskill = data.get('dataskill')
        result['ListSkills'] = addSkill(json.loads(dataskill))
    elif action == 'OpenEl':
        element = data.get('element')
        result['phrase'] = getPhrase(int(element))
    elif action == 'PrevEl':
        element = data.get('element')
        result['phrase'] = PrevPhrase(int(element))
    elif action == 'NextEl':
        element = data.get('element')
        result['phrase'] = NextPhrase(int(element))
    elif action == 'getNers':
        result['ners'] = getNers()
    elif action == 'nero_refresh':
        phrase_id = int(data.get('id'))
        updateNers(phrase_id)
        result['phrase'] = getPhrase(phrase_id)
    elif action == 'savePhrase':
        phrase_id = int(data.get('id'))
        valid = data.get('valid')
        skills = json.loads(data.get('skills'))
        ners = json.loads(data.get('ners'))
        phraseUpdate(phrase_id, valid, skills, ners)
    elif action == 'addNer':
        ner = data.get('ner')
        addNer(ner)
        result['ners'] = getNers()


    resp = JsonResponse(result, safe=False)
    resp['Access-Control-Allow-Origin'] = '*'
    return resp