# digg_paginator.py 
# copied from http://blog.localkinegrinds.com/2007/09/06/digg-style-pagination-in-django/

from django import template
 
register = template.Library()
 
LEADING_PAGE_RANGE_DISPLAYED = TRAILING_PAGE_RANGE_DISPLAYED = 10
LEADING_PAGE_RANGE = TRAILING_PAGE_RANGE = 8
NUM_PAGES_OUTSIDE_RANGE = 2 
ADJACENT_PAGES = 4
 
def digg_paginator(context):
    if (context['pages']):
        in_leading_range = in_trailing_range = False
        pages_outside_leading_range = pages_outside_trailing_range = range(0)
 
        if (context["pages"] <= LEADING_PAGE_RANGE_DISPLAYED):
            in_leading_range = in_trailing_range = True
            page_numbers = [n for n in range(1, context["pages"] + 1) if n > 0 and n <= context["pages"]]           
        elif (context["page"] <= LEADING_PAGE_RANGE):
            in_leading_range = True
            page_numbers = [n for n in range(1, LEADING_PAGE_RANGE_DISPLAYED + 1) if n > 0 and n <= context["pages"]]
            pages_outside_leading_range = [n + context["pages"] for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
        elif (context["page"] > context["pages"] - TRAILING_PAGE_RANGE):
            in_trailing_range = True
            page_numbers = [n for n in range(context["pages"] - TRAILING_PAGE_RANGE_DISPLAYED + 1, context["pages"] + 1) if n > 0 and n <= context["pages"]]
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
        else: 
            page_numbers = [n for n in range(context["page"] - ADJACENT_PAGES, context["page"] + ADJACENT_PAGES + 1) if n > 0 and n <= context["pages"]]
            pages_outside_leading_range = [n + context["pages"] for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
            pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
        return {
            "get_args": context.get("get_args",''),
            "is_paginated": context["is_paginated"],
            "previous": context["previous"],
            "has_previous": context["has_previous"],
            "next": context["next"],
            "next_page_num": context["page"] + 1,
            "has_next": context["has_next"],
            "results_per_page": context["results_per_page"],
            "page": context["page"],
            "pages": context["pages"],
            "page_numbers": page_numbers,
            "in_leading_range" : in_leading_range,
            "in_trailing_range" : in_trailing_range,
            "pages_outside_leading_range": pages_outside_leading_range,
            "pages_outside_trailing_range": pages_outside_trailing_range
        }
 
register.inclusion_tag("digg_paginator/digg_paginator.html", takes_context=True)(digg_paginator)