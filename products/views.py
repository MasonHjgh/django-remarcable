from collections import defaultdict

from django.db.models import Count, Q
from django.shortcuts import render

from .models import Category, Product, Tag


def _parse_id(value):
    """Convert a query-string value to an int, or None if it isn't a valid number."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _children_map():
    """
    Load every category in ONE query and group them by parent_id.
    Top-level categories end up under the key None.
    """
    children = defaultdict(list)
    for category in Category.objects.all():
        children[category.parent_id].append(category)
    return children


def _descendant_ids(children, root_id):
    """Return root_id plus the ids of all categories nested under it."""
    ids = [root_id]
    stack = [root_id]
    while stack:
        current = stack.pop()
        for child in children[current]:
            ids.append(child.id)
            stack.append(child.id)
    return ids


def _flatten_tree(children, parent_id=None, depth=0):
    """Yield (category, depth) in tree order, for an indented dropdown."""
    for category in children[parent_id]:
        yield category, depth
        yield from _flatten_tree(children, category.id, depth + 1)


def product_list(request):
    """Search products by text and filter them by category and tags."""
    query = request.GET.get("q", "").strip()
    category_id = _parse_id(request.GET.get("category"))
    tag_ids = {
        tag_id
        for tag_id in (_parse_id(v) for v in request.GET.getlist("tags"))
        if tag_id is not None
    }

    children = _children_map()

    products = Product.objects.select_related("category").prefetch_related("tags")

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category_id is not None:
        products = products.filter(
            category_id__in=_descendant_ids(children, category_id)
        )

    if tag_ids:
        # AND semantics: count how many of the selected tags each product has,
        # and keep only products that have all of them.
        products = products.annotate(
            matched_tags=Count("tags", filter=Q(tags__in=tag_ids), distinct=True)
        ).filter(matched_tags=len(tag_ids))

    context = {
        "products": products,
         "category_options": [
            (category.id, "— " * depth + category.name)
            for category, depth in _flatten_tree(children)
        ],
        "tags": Tag.objects.all(),
        "query": query,
        "selected_category": category_id,
        "selected_tags": tag_ids,
    }
    return render(request, "products/product_list.html", context)