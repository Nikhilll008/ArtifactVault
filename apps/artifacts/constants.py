CATEGORY_CHOICES = [
    ('Weaponry', 'Weaponry'),
    ('Coins & Currency', 'Coins & Currency'),
    ('Fort Models', 'Fort Models'),
    ('Temple Sculptures', 'Temple Sculptures'),
    ('Manuscripts', 'Manuscripts'),
    ('Costumes & Textiles', 'Costumes & Textiles'),
]

STATUS_CHOICES = [
    ('Displayed', 'Displayed'),
    ('In Storage', 'In Storage'),
    ('On Loan', 'On Loan'),
]

ICON_CHOICES = [
    ('sword', 'sword'),
    ('coin', 'coin'),
    ('fort', 'fort'),
    ('sculpture', 'sculpture'),
    ('manuscript', 'manuscript'),
    ('costume', 'costume'),
]

CSV_FIELDS = [
    'id', 'name', 'category', 'icon', 'era', 'eraGroup', 'material',
    'materialGroup', 'origin', 'originGroup', 'status', 'dateAdded',
    'dimensions', 'significance',
]
