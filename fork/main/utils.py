from fork.models import ForkCategory


def prepare_creation_data(request):
    """"Categories  are going to be predefined, so that users can only choose from suggested ones,
        this will be marked as 'Uncategorized' otherwise.

        If all([name, description, creation_date, category in [category.category for category in ForkCategory.query.all()]]):
        checks whether all needed parameters are present in json body AND that provided category is within already existing ones
    """
    name = request.get('name', None)
    description = request.get('description', None)
    creation_date = request.get('creation_date', None)
    category = request.get('category', 'Uncategorized')
    if all([name, description, creation_date, category in [category.category for category in ForkCategory.query.all()]]):
        result = {'name': name,
                  'description': description,
                  'creation_date': creation_date,
                  'category': category
                  }
        return result
    return False  # False means that given data is invalid in some way
