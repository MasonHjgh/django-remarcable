# Product Search (Django)

A Django project that models products, categories and tags, and provides a page for searching products by text and filtering them by category and tags. Search and filters can be combined freely.

## Features

- **Search** products by name or description (case-insensitive).
- **Filter by category**, including all of its subcategories (selecting "Electronics" also shows products in "Monitors").
- **Filter by tags**, where a product must have **all** selected tags.
- Any combination of search and filters, with the form remembering the current selections.
- Customized Django admin for managing categories, tags and products.

## Requirements

- Python 3.10 or newer
- Django (version pinned in `requirements.txt`)

## Setup

1. **Clone the repository**

   ```
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Create and activate a virtual environment**

   ```
   python -m venv venv
   ```

   - Windows (PowerShell): `venv\Scripts\activate`
   - macOS / Linux: `source venv/bin/activate`

3. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```

4. **Create the database tables**

   ```
   python manage.py migrate
   ```

5. **Load the sample data** 

   adding sample data from the admin interface manually wouldn't be efficient so I used a seeder to insert them. 

   - With the seed command (safe to run more than once):

     ```
     python manage.py seed_products
     ```

6. **Create an admin user**

   ```
   python manage.py createsuperuser
   ```

7. **Run the development server**

   ```
   python manage.py runserver
   ```

   - Product search page: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Running the tests

no tests have been written per the assignment requirements

```
python manage.py test
```
## Data model

```
Category ──< Product >──< Tag
   │
   └── parent (self-referencing, optional)
```

- **Category**: `name` (globally unique), `description`, optional `parent` (another Category).
- **Tag**: `name` (unique).
- **Product**: `name`, `description`, `price`, `created_at`, a ForeignKey to **Category** and a ManyToMany to **Tag**.

### Why these relationships

- **Category is a ForeignKey (one-to-many).** A category describes *what a product is*, so each product has a single primary category, while a category contains many products. Enforcing this in the schema keeps "which category is this in?" to a single answer and avoids double-counting when grouping by category. 
- **Tags are ManyToMany.** Tags describe *attributes* that cut across categories (e.g. "waterproof" applies to a phone and a dog jacket), and a product can have any number of them.
- **Categories are nested** through a self-referencing `parent` ForeignKey, which allows a hierarchy such as Electronics → Monitors.

PS: also tags could be used on categories as well, in fact we could have used the tags as a general labeling feature for any entity required. it would make searching and indexing easier in some cases. 
the Category also could have a many-to-many relation ship with products but in this case it could have been mistaken with tags. either way depending on business logic both can be implemented. 


## Design decisions and assumptions

- **Tag filtering uses AND logic.** Selecting several tags narrows the results to products that have every selected tag. This is implemented with a conditional `Count` annotation compared against the number of selected tags, which returns one row per product, so no `.distinct()` is needed. OR logic would be `filter(tags__in=ids).distinct()`.
- **Search covers name and description**, combined with a `Q` object, using `icontains`.
- **Category filtering includes subcategories.** All categories are loaded in a single query and arranged into a parent → children map in Python; the selected category's descendants are collected from that map and filtered with `category_id__in`. This is efficient for a small catalogue. For large trees, a package such as `django-mptt` or `django-treebeard` would allow fetching subtrees in a single query.
- **Category names are globally unique**, even across different parents (e.g. "Electronics Accessories" rather than two categories named "Accessories").
- **Deleting a category is protected** (`on_delete=PROTECT`): a category that still has products or subcategories cannot be deleted, to avoid accidentally deleting products or entire subtrees. (This can be changed so that if a category is deleted, either user would be prompted to choose a category to move the products to, or simple just make the category id nullable on product and call the products with no category as uncategorized.)
- **Circular category hierarchies are prevented** by `Category.clean()`, which rejects a parent that is the category itself or one of its descendants. This validation runs in the admin and other model forms.
- **Prices use `DecimalField`** rather than `FloatField` to avoid floating-point rounding errors with money.
- **Query efficiency:** the product list uses `select_related("category")` and `prefetch_related("tags")` to avoid N+1 queries, and the admin uses `Count` annotations for its product-count columns instead of counting per row.


## Project structure

```
config/                     Project settings and root URLs
products/
├── admin.py                Admin configuration
├── models.py               Category, Tag, Product
├── views.py                Search and filter view
├── urls.py                 App URLs
├── tests.py                Tests for search and filtering
├── fixtures/
│   └── sample_data.json    Sample data
├── management/commands/
│   └── seed_products.py    Seed command
└── templates/products/
    └── product_list.html   Search page
```

## Possible improvements

- Pagination of results.
- A toggle between AND and OR tag matching.

## AI usage

AI was used to produce the sample data in the seeder, also as a teacher as it was my first django project so I need to understand the similarities and differences between Laravel(my mostly used framwork nowadays) and django. AI auto complete has been also used in VS code. 

