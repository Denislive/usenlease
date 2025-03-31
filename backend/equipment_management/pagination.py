from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param
import math
from urllib.parse import urlparse, urlunparse

class CustomEquipmentPagination(PageNumberPagination):
    """
    Custom pagination that enforces HTTPS for ALL URLs (prev, next, page links)
    """
    page_size = 120  
    page_size_query_param = "page_size"
    max_page_size = 1000 

    def enforce_https(self, url):
        """Force HTTPS for any URL if the original request was secure"""
        if not url:
            return url
            
        if self.request and self.request.is_secure():
            parsed = urlparse(url)
            if parsed.scheme == 'http':
                return urlunparse(parsed._replace(scheme='https'))
        return url

    def get_page_link(self, page_number):
        """Generate HTTPS URL for a specific page number"""
        if not self.request:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.page_query_param, page_number)
        return self.enforce_https(url)

    def get_next_link(self):
        """Override to ensure HTTPS in next link"""
        url = super().get_next_link()
        return self.enforce_https(url)

    def get_previous_link(self):
        """Override to ensure HTTPS in previous link"""
        url = super().get_previous_link()
        return self.enforce_https(url)

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)
        current_page = self.page.number
        total_items = self.page.paginator.count

        # Generate numbered page links with HTTPS enforcement
        page_links = [
            {
                "page": i,
                "label": i * self.page_size,  
                "url": self.get_page_link(i),  # HTTPS enforced here
            }
            for i in range(1, total_pages + 1)
        ]

        return Response({
            "count": total_items,
            "total_pages": total_pages,
            "current_page": current_page,
            "next": self.get_next_link(),          # HTTPS enforced
            "previous": self.get_previous_link(),  # HTTPS enforced
            "page_links": page_links,             # All HTTPS
            "results": data,
        })