"""
CONCEPT: DRF
--------------
Note these are plain `serializers.Serializer` subclasses, not
`ModelSerializer` — there's no Django model behind artifacts (the data
lives in MongoDB), so every field is declared explicitly and validated
data is handed to ArtifactRepository as a dict.
"""
from rest_framework import serializers
from .constants import CATEGORY_CHOICES, STATUS_CHOICES, ICON_CHOICES


class ArtifactSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=150)
    category = serializers.ChoiceField(choices=CATEGORY_CHOICES)
    icon = serializers.ChoiceField(choices=ICON_CHOICES, required=False, default='sword')
    era = serializers.CharField(max_length=150)
    eraGroup = serializers.CharField(max_length=80)
    material = serializers.CharField(max_length=150)
    materialGroup = serializers.CharField(max_length=80)
    origin = serializers.CharField(max_length=150)
    originGroup = serializers.CharField(max_length=80)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False, default='In Storage')
    dateAdded = serializers.CharField(read_only=True)
    dimensions = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    significance = serializers.CharField()
