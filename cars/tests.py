from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Car, Rating


class CarsTests(APITestCase):
    def setUp(self):
        self.car_item_1 = Car.objects.create(make='BMW', model="320i")
        self.car_item_2 = Car.objects.create(make='BMW', model="325i")
        self.car_item_3 = Car.objects.create(make='BMW', model="328i")
        self.car_item_4 = Car.objects.create(make='BMW', model="330i")
        self.car_item_5 = Car.objects.create(make='BMW', model="335i")

    def test_get_cars(self):
        url = reverse('car_list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Car.objects.count(), 5)

    def test_post_cars(self):
        url = reverse('car_list')
        data = {'make': 'BMW', 'model': '530i'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_cars_duplicate(self):
        url = reverse('car_list')
        data = {'make': 'BMW', 'model': '330i'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_cars_make_doesnt_exist(self):
        url = reverse('car_list')
        data = {'make': 'DOES_NOT_EXIST', 'model': '330i'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_post_cars_model_doesnt_exist(self):
        url = reverse('car_list')
        data = {'make': 'BMW', 'model': 'DOES_NOT_EXIST'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_cars_body_not_valid1(self):
        url = reverse('car_list')
        data = {'NOT_VALID': 'BMW', 'model': '330i'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_cars_body_not_valid2(self):
        url = reverse('car_list')
        data = {'make': 'BMW', 'NOT_VALID': '330i'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_cars_body_not_valid3(self):
        url = reverse('car_list')
        data = {'NOT_VALID': 'BMW', 'NOT_VALID': '330i'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_cars_body_too_much_arguments(self):
        url = reverse('car_list')
        data = {'make': 'BMW', 'model': '340i', 'ADDITIONAL_KEY': 'SHOULD_WORK_FINE'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    

class CarsDeleteTests(APITestCase):
    def setUp(self):
        self.car_item_1 = Car.objects.create(make='BMW', model="320i")

    def test_delete_cars(self):
        response = self.client.delete('/cars/1/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_cars_not_in_database(self):
        response = self.client.delete('/cars/2/', format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RatingTests(APITestCase):
    def setUp(self):
        self.car_item_1 = Car.objects.create(make='BMW', model="320i")
        self.car_1_rating_1 = Rating.objects.create(car_id=self.car_item_1, rating='1')

    def test_add_rating(self):
        data = {'car_id': '1', 'rating': '5'}
        response = self.client.post('/rate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        #check if average rating is calculated and saved properly
        self.assertEqual(Car.objects.get(id=1).avg_rating, 3)
    
    def test_add_rating_item_doesnt_exist(self):
        data = {'car_id': '2', 'rating': '5'}
        response = self.client.post('/rate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_rating_rating_too_high(self):
        data = {'car_id': '1', 'rating': '6'}
        response = self.client.post('/rate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_rating_rating_too_low(self):
        data = {'car_id': '1', 'rating': '0'}
        response = self.client.post('/rate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_rating_rating_not_int(self):
        data = {'car_id': '1', 'rating': '3.5'}
        response = self.client.post('/rate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_rating_body_not_valid1(self):
        data = {'NOT_VALID': '1', 'rating': '5'}
        response = self.client.post('/rate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_rating_body_not_valid2(self):
        data = {'car_id': '1', 'NOT_VALID': '5'}
        response = self.client.post('/rate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_rating_body_not_valid3(self):
        data = {'NOT_VALID': '1', 'NOT_VALID': '5'}
        response = self.client.post('/rate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_rating_too_much_arguments(self):
        data = {'car_id': '1', 'rating': '5', 'ADDITIONAL_KEY': 'SHOULD_WORK_FINE'}
        response = self.client.post('/rate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class PopularTests(APITestCase):
    def setUp(self):
        self.car_item_1 = Car.objects.create(make='BMW', model="320i")
        # add 1 rating to car_id 1
        self.car_1_rating_1 = Rating.objects.create(car_id=self.car_item_1, rating='5')


        self.car_item_2 = Car.objects.create(make='BMW', model="325i")
        # add 2 ratings to car_id 2
        self.car_2_rating_1 = Rating.objects.create(car_id=self.car_item_2, rating='5')
        self.car_2_rating_2 = Rating.objects.create(car_id=self.car_item_2, rating='5')

    def test_add_rating(self):
        url = reverse('popular')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #check if items are displayed in the correct order
        self.assertEqual(response.data[0]['id'], 2)