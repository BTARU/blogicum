from typing import Any

from django.core.paginator import Paginator


def paginate(request, objects: Any, num_to_show: int):
    """Return pagination object."""
    return Paginator(
        objects, num_to_show
    ).get_page(
        request.GET.get('page')
    )
