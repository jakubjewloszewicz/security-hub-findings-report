

from jinja2 import Environment, FileSystemLoader

jinja_env = Environment(loader=FileSystemLoader('src/to_markdown/templates'))

# Custom filter for regex search
def regex_search(value, pattern):
    """Extract groups from regex pattern match."""
    import re
    match = re.search(pattern, value)
    if match:
        return match.groups()
    return None

jinja_env.filters['regex_search'] = regex_search

class MarkdownPrinter:

    @property
    def template(self):
        if not hasattr(self, 'template_name') or not self.template_name:
            raise AttributeError("Subclasses must define a 'template_name' attribute.")
        return jinja_env.get_template(self.template_name)

    def to_markdown(self, account_id, region_name, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement to_markdown method")
