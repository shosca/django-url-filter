# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from django.http import Http404
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet

from url_filter.backends.plain import PlainFilterBackend
from url_filter.backends.sqlalchemy import SQLAlchemyFilterBackend
from url_filter.filtersets import ModelFilterSet
from url_filter.filtersets.plain import PlainModelFilterSet
from url_filter.filtersets.sqlalchemy import SQLAlchemyModelFilterSet

from . import alchemy
from .models import Place, Restaurant, Waiter


class PlaceSerializer(ModelSerializer):
    class Meta(object):
        model = Place


class RestaurantSerializer(ModelSerializer):
    place = PlaceSerializer()

    class Meta(object):
        model = Restaurant


class WaiterNestedSerializer(ModelSerializer):
    restaurant = RestaurantSerializer()

    class Meta(object):
        model = Waiter


class WaiterSerializer(ModelSerializer):
    class Meta(object):
        model = Waiter


class RestaurantNestedSerializer(ModelSerializer):
    place = PlaceSerializer()
    waiters = WaiterSerializer(source='waiter_set', many=True)

    class Meta(object):
        model = Restaurant


class RestaurantNestedWithoutPlaceSerializer(ModelSerializer):
    waiters = WaiterSerializer(source='waiter_set', many=True)

    class Meta(object):
        model = Restaurant


class PlaceNestedSerializer(ModelSerializer):
    restaurant = RestaurantNestedWithoutPlaceSerializer()

    class Meta(object):
        model = Place


class PlaceFilterSet(ModelFilterSet):
    class Meta(object):
        model = Place


class PlainPlaceFilterSet(PlainModelFilterSet):
    filter_backend_class = PlainFilterBackend

    class Meta(object):
        model = {
            "id": 1,
            "restaurant": {
                "place": 1,
                "waiters": [
                    {
                        "id": 1,
                        "name": "Joe",
                        "restaurant": 1
                    },
                    {
                        "id": 2,
                        "name": "Jonny",
                        "restaurant": 1
                    }
                ],
                "serves_hot_dogs": True,
                "serves_pizza": False
            },
            "name": "Demon Dogs",
            "address": "944 W. Fullerton"
        }


class SQLAlchemyPlaceFilterSet(SQLAlchemyModelFilterSet):
    filter_backend_class = SQLAlchemyFilterBackend

    class Meta(object):
        model = alchemy.Place


class RestaurantFilterSet(ModelFilterSet):
    class Meta(object):
        model = Restaurant


class SQLAlchemyRestaurantFilterSet(SQLAlchemyModelFilterSet):
    filter_backend_class = SQLAlchemyFilterBackend

    class Meta(object):
        model = alchemy.Restaurant


class WaiterFilterSet(ModelFilterSet):
    class Meta(object):
        model = Waiter


class SQLAlchemyWaiterFilterSet(SQLAlchemyModelFilterSet):
    filter_backend_class = SQLAlchemyFilterBackend

    class Meta(object):
        model = alchemy.Waiter


class PlaceViewSet(ReadOnlyModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceNestedSerializer
    filter_class = PlaceFilterSet


class PlainPlaceViewSet(ReadOnlyModelViewSet):
    serializer_class = PlaceNestedSerializer
    queryset = Place.objects.all()
    filter_class = PlainPlaceFilterSet

    def get_queryset(self):
        qs = super(PlainPlaceViewSet, self).get_queryset()
        data = self.get_serializer(instance=qs.all(), many=True).data
        return data

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(queryset)

    def retrieve(self, request, pk):
        instance = next(
            iter(filter(lambda i: i.get('id') == int(pk),
                        self.get_queryset())),
            None
        )
        if not instance:
            raise Http404
        return Response(instance)


class SQLAlchemyPlaceViewSet(ReadOnlyModelViewSet):
    serializer_class = PlaceNestedSerializer
    filter_class = SQLAlchemyPlaceFilterSet

    def get_queryset(self):
        return self.request.alchemy_session.query(alchemy.Place)


class RestaurantViewSet(ReadOnlyModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantNestedSerializer
    filter_class = RestaurantFilterSet


class SQLAlchemyRestaurantViewSet(ReadOnlyModelViewSet):
    serializer_class = RestaurantNestedSerializer
    filter_class = SQLAlchemyRestaurantFilterSet

    def get_queryset(self):
        return self.request.alchemy_session.query(alchemy.Restaurant)


class WaiterViewSet(ReadOnlyModelViewSet):
    queryset = Waiter.objects.all()
    serializer_class = WaiterNestedSerializer
    filter_class = WaiterFilterSet


class SQLAlchemyWaiterViewSet(ReadOnlyModelViewSet):
    serializer_class = WaiterNestedSerializer
    filter_class = SQLAlchemyWaiterFilterSet

    def get_queryset(self):
        return self.request.alchemy_session.query(alchemy.Waiter)
