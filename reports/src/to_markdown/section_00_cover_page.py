
from datetime import datetime
from src.to_markdown.markown_printer import MarkdownPrinter


class CoverPageSection(MarkdownPrinter):

    template_name = "section_00_cover_page.md.j2"
    
    def to_markdown(self, account_id, region_name, *args, **kwargs):
        generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return [self.template.render(
            account_id=account_id,
            generation_time=generation_time
        )]

