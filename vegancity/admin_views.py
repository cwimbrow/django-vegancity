# Copyright (C) 2012 Steve Lamb

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

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

import forms
import models
import itertools

def pending_approval(request):
    pending_vendors = models.Vendor.approved_objects.pending_approval()
    pending_reviews = models.Review.objects.filter(approved=False)
    ctx = {
        'pending_vendors' : pending_vendors,
        'pending_reviews' : pending_reviews,
        }
    return render_to_response("admin/pending_approval.html", ctx,
                              context_instance=RequestContext(request))
