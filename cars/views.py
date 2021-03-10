import requests
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet

from cars.models import Car, Rating
from cars.serializers import (CarPopularSerializer, CarSerializer,
                              RatingSerializer)


class RemoteAPIException(ValidationError):
    #raise API exceptions with custom messages and custom status codes
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'error'

    def __init__(self, detail, status_code=None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code


def car_exists(data):
    try: 
        #get car models list from https://vpic.nhtsa.dot.gov/api/
        model_list = requests.get(f'https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/{data["make"]}?format=json').json()
    except:
        raise RemoteAPIException('vpic.nhtsa.dot.gov/api does not respond, try again later.', status_code=status.HTTP_404_NOT_FOUND)

    for model in model_list['Results']:
        #check if submitted car model exists in fetched models list
        if data['model'] == model['Model_Name']:
            return True

    return False


@api_view(['GET', 'POST'])
def car_list(request):
    if request.method == 'GET':
        cars = Car.objects.all()
        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = CarSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            #check if submitted car already exists in database
            if Car.objects.filter(make=serializer.validated_data['make'], model=serializer.validated_data['model']).exists():
                return Response({"detail": "Car already exists in database."}, status=status.HTTP_400_BAD_REQUEST)

            #check if submitted car model exists at all
            if not car_exists(serializer.validated_data):
                return Response({"detail": "Car doesn't exist."}, status=status.HTTP_400_BAD_REQUEST)
                
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def car_delete(request, pk):
    #check if item exists in database
    try:
        cars = Car.objects.get(id=pk)
    except:
        return Response({"detail": "Item does not exist."}, status=status.HTTP_404_NOT_FOUND)
    
    cars.delete()
    return Response({"detail": "Item deleted."}, status=status.HTTP_200_OK)


@api_view(['POST'])
def rate_car(request):
    serializer = RatingSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        car = Car.objects.get(pk=request.data['car_id'])

        #create new rating item for submitted car id
        serializer.save(car_id=car)

        avg_rating=0
        for rating in Rating.objects.filter(car_id=serializer.validated_data['car_id']):
            avg_rating += rating.rating

        avg_rating=round(avg_rating/len(Rating.objects.filter(car_id=serializer.validated_data['car_id'])),2)
        
        #update average rating for submitted car id
        car.avg_rating=avg_rating
        car.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def car_popular(request):
    #list car items ordered by ratings count
    cars = Car.objects.all().annotate(ratings_count=Count('ratings')).order_by('-ratings_count')
    serializer = CarPopularSerializer(cars, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
