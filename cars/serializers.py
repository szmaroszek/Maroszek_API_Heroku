from rest_framework.serializers import ModelSerializer, SerializerMethodField

from cars.models import Car, Rating


class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = ['car_id', 'rating',]


class CarSerializer(ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'make', 'model', 'avg_rating',]


class CarPopularSerializer(ModelSerializer):
    rates_number = SerializerMethodField()
    
    def get_rates_number(self, obj):
        return obj.ratings.count()
        
    class Meta:
        model = Car
        fields = ['id', 'make', 'model', 'rates_number',]
