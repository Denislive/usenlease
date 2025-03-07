from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param  # ✅ Import this function
import math

class CustomEquipmentPagination(PageNumberPagination):
    """
    Custom pagination to show previous, next, and page links for every 100 items.
    """
    page_size = 120  
    page_size_query_param = "page_size"
    max_page_size = 1000 

    def get_page_link(self, page_number):
        """
        Generate the full URL for a given page number.
        """
        if not self.request:
            return None

        url = self.request.build_absolute_uri()
        return replace_query_param(url, self.page_query_param, page_number)  # ✅ Fix here

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)
        current_page = self.page.number
        total_items = self.page.paginator.count

        # Generate numbered page links
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
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "page_links": page_links,  
            "results": data,
        })
