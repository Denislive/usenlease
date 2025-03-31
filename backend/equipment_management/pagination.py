from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param
import math

class CustomEquipmentPagination(PageNumberPagination):
    """
    Custom pagination to ensure HTTPS for all pagination URLs.
    """
    page_size = 120  
    page_size_query_param = "page_size"
    max_page_size = 1000 

    def enforce_https(self, url):
        """Ensure the URL uses HTTPS if the request was secure."""
        if url and self.request and self.request.is_secure():
            return url.replace('http://', 'https://', 1)
        return url

    def get_page_link(self, page_number):
        """
        Generate the full URL for a given page number (ensures HTTPS).
        """
        if not self.request:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.page_query_param, page_number)
        return self.enforce_https(url)

    def get_next_link(self):
        """Override to ensure HTTPS in next link."""
        url = super().get_next_link()
        return self.enforce_https(url)

    def get_previous_link(self):
        """Override to ensure HTTPS in previous link."""
        url = super().get_previous_link()
        return self.enforce_https(url)

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)
        current_page = self.page.number
        total_items = self.page.paginator.count

        # Generate numbered page links (HTTPS enforced via get_page_link)
        page_links = [
            {
                "page": i,
                "label": i * self.page_size,  
                "url": self.get_page_link(i),
            }
            for i in range(1, total_pages + 1)
        ]

        return Response({
            "count": total_items,
            "total_pages": total_pages,
            "current_page": current_page,
            "next": self.get_next_link(),  # HTTPS enforced
            "previous": self.get_previous_link(),  # HTTPS enforced
            "page_links": page_links,  
            "results": data,
        })