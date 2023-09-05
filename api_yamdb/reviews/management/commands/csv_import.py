import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from reviews.models import Category, Title, Comment, Genre, GenreTitle, Review
from users.models import User

class Command(BaseCommand):
    help = 'Import data from CSV files'

    CSV_DIRECTORY = os.path.join(settings.STATICFILES_DIRS[0], 'data/')
    CSV_FILES = {
        'users': 'users.csv',
        'category': 'category.csv',
        'genre': 'genre.csv',
        'titles': 'titles.csv',
        'genre_title': 'genre_title.csv',
        'reviews': 'review.csv',
        'comments': 'comments.csv',
    }

    def handle(self, *args, **kwargs):
        self.import_users()
        self.import_categories()
        self.import_genres()
        self.import_titles()
        self.import_genre_titles()
        self.import_reviews()
        self.import_comments()
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))

    def import_users(self):
        users_csv_path = os.path.join(self.CSV_DIRECTORY, self.CSV_FILES['users'])
        with open(users_csv_path, 'r') as users_file:
            csv_reader = csv.DictReader(users_file)
            users_to_create = []
            for row in csv_reader:
                user_id = row['id']
                if not User.objects.filter(id=user_id).exists():
                    users_to_create.append(User(
                        id=user_id,
                        username=row['username'],
                        email=row['email'],
                        role=row['role'],
                        bio=row['bio'],
                        first_name=row['first_name'],
                        last_name=row['last_name']
                    ))
            User.objects.bulk_create(users_to_create)
        self.stdout.write(self.style.SUCCESS('Users data imported successfully'))

    def import_categories(self):
        category_csv_path = os.path.join(self.CSV_DIRECTORY, self.CSV_FILES['category'])
        with open(category_csv_path, 'r') as category_file:
            csv_reader = csv.DictReader(category_file)
            categories_to_create = []
            for row in csv_reader:
                categories_to_create.append(Category(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                ))
            Category.objects.bulk_create(categories_to_create)
        self.stdout.write(self.style.SUCCESS('Categories data imported successfully'))

    def import_genres(self):
        genre_csv_path = os.path.join(self.CSV_DIRECTORY, self.CSV_FILES['genre'])
        with open(genre_csv_path, 'r') as genre_file:
            csv_reader = csv.DictReader(genre_file)
            genres_to_create = []
            for row in csv_reader:
                genres_to_create.append(Genre(
                    id=row['id'],
                    name=row['name'],
                    slug=row['slug']
                ))
            Genre.objects.bulk_create(genres_to_create)
        self.stdout.write(self.style.SUCCESS('Genres data imported successfully'))

    def import_titles(self):
        titles_csv_path = os.path.join(self.CSV_DIRECTORY, self.CSV_FILES['titles'])
        with open(titles_csv_path, 'r') as title_file:
            csv_reader = csv.DictReader(title_file)
            titles_to_create = []
            for row in csv_reader:
                titles_to_create.append(Title(
                    id=row['id'],
                    name=row['name'],
                    year=row['year'],
                    category_id=row['category'],
                ))
            Title.objects.bulk_create(titles_to_create)
        self.stdout.write(self.style.SUCCESS('Titles data imported successfully'))

    def import_genre_titles(self):
        genre_title_csv_path = os.path.join(self.CSV_DIRECTORY, self.CSV_FILES['genre_title'])
        with open(genre_title_csv_path, 'r') as genre_title_file:
            csv_reader = csv.DictReader(genre_title_file)
            genre_titles_to_create = []
            for row in csv_reader:
                genre_titles_to_create.append(GenreTitle(
                    id=row['id'],
                    title_id=row['title_id'],
                    genre_id=row['genre_id'],
                ))
            GenreTitle.objects.bulk_create(genre_titles_to_create)
        self.stdout.write(self.style.SUCCESS('Genre Titles data imported successfully'))

    def import_reviews(self):
        reviews_csv_path = os.path.join(self.CSV_DIRECTORY, self.CSV_FILES['reviews'])
        with open(reviews_csv_path, 'r') as reviews_file:
            csv_reader = csv.DictReader(reviews_file)
            reviews_to_create = []
            for row in csv_reader:
                reviews_to_create.append(Review(
                    id=row['id'],
                    title_id=row['title_id'],
                    text=row['text'],
                    author_id=row['author'],
                    score=row['score'],
                    pub_date=row['pub_date']
                ))
            Review.objects.bulk_create(reviews_to_create)
        self.stdout.write(self.style.SUCCESS('Reviews data imported successfully'))

    def import_comments(self):
        comments_csv_path = os.path.join(self.CSV_DIRECTORY, self.CSV_FILES['comments'])
        with open(comments_csv_path, 'r') as comments_file:
            csv_reader = csv.DictReader(comments_file)
            comments_to_create = []
            for row in csv_reader:
                comments_to_create.append(Comment(
                    id=row['id'],
                    review_id=row['review_id'],
                    text=row['text'],
                    author_id=row['author'],
                    pub_date=row['pub_date']
                ))
            Comment.objects.bulk_create(comments_to_create)
        self.stdout.write(self.style.SUCCESS('Comments data imported successfully'))

