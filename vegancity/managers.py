# Copyright (C) 2014 Steve Lamb

# This file is part of Vegancity.

# Vegancity is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Vegancity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Vegancity.  If not, see <http://www.gnu.org/licenses/>.


import random

from django.contrib.gis.db import models
from django.db.models import Count

from djorm_pgfulltext.models import SearchManagerMixIn, SearchQuerySet
from django.contrib.gis.db.models.query import GeoQuerySet

##########################################################>
# Managers for models that relate to vendor
##########################################################>


class SearchByVendorQuerySet(SearchQuerySet, GeoQuerySet):
    def vendor_search(self, *args, **kwargs):
        from models import Vendor
        qs = self.search(*args, **kwargs).values_list('vendor', flat=True)
        # TODO: not sure why this has to be casted to a list, but
        # caused an error without it
        vendors = Vendor.objects.approved().filter(pk__in=list(qs))
        return vendors

    def with_vendors(self, vendors=None):
        qs = self.filter(vendor__approval_status='approved')

        if not (vendors is None):
            qs = qs.filter(vendor__in=vendors)

        qs = (qs
              .distinct()
              .annotate(vendor_count=Count('vendor'))
              .filter(vendor_count__gt=0)
              .order_by('-vendor_count'))

        return qs


class SearchByVendorManager(SearchManagerMixIn, models.Manager):
    def get_queryset(self):
        return SearchByVendorQuerySet(model=self.model, using=self._db)

    # TODO: use a better pass-thru mechanism to avoid
    # repeating these qs methods on the manager

    def vendor_search(self, *args, **kwargs):
        return self.get_queryset().vendor_search(*args, **kwargs)

    def with_vendors(self, *args, **kwargs):
        return self.get_queryset().with_vendors(*args, **kwargs)


class ReviewManager(SearchByVendorManager):
    def approved(self):
        return self.get_queryset().filter(approved=True)

    def pending_approval(self):
        """returns all reviews that are not approved, which are
        otherwise impossible to get in a normal query (for now)."""
        normal_qs = self.get_queryset()
        pending = normal_qs.filter(approved=False)
        return pending


class VendorQuerySet(GeoQuerySet, SearchQuerySet):
    def pending_approval(self):
        """returns all vendors that are not approved, which are
        otherwise impossible to get in a normal query."""
        return self.filter(approval_status='pending')

    def approved(self):
        return self.filter(approval_status='approved')

    def without_reviews(self):
        from models import Review
        review_vendors = (Review
                          .objects.approved()
                          .values_list('vendor_id', flat=True))
        return self.all().exclude(pk__in=review_vendors)

    def with_reviews(self):
        return self.filter(review__approved=True)\
                   .distinct()\
                   .annotate(review_count=Count('review'))\
                   .order_by('-review_count')

    def get_random_unreviewed(self):
        try:
            return random.choice(self.without_reviews())
        except IndexError:
            return None


class VendorManager(SearchManagerMixIn, models.GeoManager):
    def get_queryset(self):
        return VendorQuerySet(model=self.model, using=self._db)

    # TODO: use a better pass-thru mechanism to avoid
    # repeating these qs methods on the manager
    def search(self, *args, **kwargs):
        return self.get_queryset().search(*args, **kwargs)

    def approved(self):
        return self.get_queryset().approved()

    def pending_approval(self):
        return self.get_queryset().pending_approval()
