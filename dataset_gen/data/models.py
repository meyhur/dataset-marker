from django.db import models

class Valid(models.Model):
    name = models.CharField('Статус', max_length=50)
    value = models.CharField('Значение', max_length=50)

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return self.name

class Skill(models.Model):
    '''
    Скилы
    '''
    name = models.CharField('Наименование умения', max_length=200)
    description = models.TextField('Описание умения', blank=True)

    class Meta:
        verbose_name = 'Скил'
        verbose_name_plural = 'Скилы'

    def __str__(self):
        return self.name

class Ner(models.Model):
    '''
    Сущности, для ner (локация, товар, дата, число)
    '''
    name = models.CharField('Наименование', max_length=200)
    description = models.TextField('Описание', blank=True)
    abbr = models.CharField('Аббревиатура', max_length=10)
    color = models.CharField(verbose_name='Color', max_length=7,
                             help_text='HEX color, as #RRGGBB')
    order = models.PositiveIntegerField('Сортировка', default=500,)

    class Meta:
        verbose_name = 'Сущность'
        verbose_name_plural = 'Сущности'

    def __str__(self):
        return self.name

class Phrase(models.Model):
    '''
    Текст датасета
    '''
    text = models.CharField('Фраза', max_length=5000)
    valid = models.ForeignKey(Valid, verbose_name="Валидное", blank=True, null=True, on_delete=models.CASCADE)
    has_parent = models.BooleanField("Есть предыдущий", blank = True, default=False)
    id_prev = models.CharField('id предыдущего', blank = True, default='', max_length=15)
    id_db = models.CharField('id в БД', blank = True, default='', max_length=15)
    skills = models.ManyToManyField(Skill, verbose_name="Скилы", blank = True)
    ners = models.TextField("Разметка фразы", blank = True)
    during = models.BooleanField("Обрабатывается", default=False)
    during_start = models.DateTimeField("Начало обработки", auto_now=True)
    processed = models.BooleanField("Размечено", default=False)

    class Meta:
        verbose_name = 'Фраза'
        verbose_name_plural = 'Фразы'
        indexes = [
            models.Index(fields=['text', 'id_db',]),
            models.Index(fields=['text',]),
            models.Index(fields=['id_prev',]),
            models.Index(fields=['id_db',]),
            models.Index(fields=['during',]),
            models.Index(fields=['during_start',]),
        ]

    def __str__(self):
        return self.text
