from rest_framework import serializers

from reviews.models import Category, Genre, Title
from reviews.validators import validate_slug 

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        validators=[validate_slug],
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        validators=[validate_slug],
    )
    class Meta:
        fields =  ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title


