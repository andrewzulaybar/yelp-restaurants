from django.db import models


class BookmarksManager(models.Manager):
    def create_bookmark(self, date, restaurant):
        return self.create(date=date, restaurant=restaurant)


class Bookmarks(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    restaurant = models.ForeignKey(
        'Restaurant',
        on_delete=models.CASCADE
    )

    objects = BookmarksManager()


class CategoryManager(models.Manager):
    def create_category(self, title, alias):
        return self.create(title=title, alias=alias)


class Category(models.Model):
    title = models.CharField(max_length=20, primary_key=True)
    alias = models.CharField(max_length=20)

    objects = CategoryManager()


class LocationManager(models.Manager):
    def create_location(self, location):
        return self.create(
            address=location['address'], city=location['city'], province=location['province'],
            country=location['country'], postal_code=location['postal_code'],
            latitude=location['latitude'], longitude=location['longitude']
        )


class Location(models.Model):
    address = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    province = models.CharField(max_length=2)
    country = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=7)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        unique_together = (('address', 'postal_code'),)

    objects = LocationManager()


class RestaurantManager(models.Manager):
    def create_restaurant(self, restaurant):
        return self.create(
            business_id=restaurant['business_id'], name=restaurant['name'], rating=restaurant['rating'],
            review_count=restaurant['review_count'], price=restaurant['price'], phone=restaurant['phone'],
            image_url=restaurant['image_url'], yelp_url=restaurant['yelp_url'], location=restaurant['location']
        )


class Restaurant(models.Model):
    business_id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=50)
    rating = models.DecimalField(decimal_places=1, max_digits=2)
    review_count = models.IntegerField()
    price = models.CharField(max_length=4, blank=True, null=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    image_url = models.CharField(max_length=300, blank=True, null=True)
    yelp_url = models.CharField(max_length=300)
    location = models.ForeignKey(
        'Location',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    objects = RestaurantManager()


class RestaurantHasCategoryManager(models.Manager):
    def create_object(self, restaurant, category):
        return self.create(restaurant=restaurant, category=category)


class RestaurantHasCategory(models.Model):
    restaurant = models.ForeignKey(
        'Restaurant',
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE
    )
    objects = RestaurantHasCategoryManager()

    class Meta:
        unique_together = (('restaurant', 'category'),)


class VisitedManager(models.Manager):
    def create_visited(self, restaurant):
        return self.create(restaurant=restaurant)


class Visited(models.Model):
    restaurant = models.ForeignKey(
        'Restaurant',
        on_delete=models.CASCADE
    )

    objects = VisitedManager()
