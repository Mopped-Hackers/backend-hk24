from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import json
import re
from ...models import DataStory
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


class PdfGenerator:
    def __init__(self,app:FastAPI, story: DataStory) -> None:

        # Get the root path
        root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Create the uploads folder if it doesn't exist
        uploads_folder = os.path.join(root_path, 'uploads')
        if not os.path.exists(uploads_folder):
            os.makedirs(uploads_folder)

        # Mount the directory as a static files directory
        app.mount("/static", StaticFiles(directory=uploads_folder), name="static")
        
        
        self.filename = os.path.join(uploads_folder,f"./structured_output_{story.url}_{story.id}.pdf")

        
        self.story: DataStory = story

        self.doc = SimpleDocTemplate(self.filename, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.text_style = self.styles['Normal']
        self.flowables = []
    

    def generate_pdf(self):
        data = self.story.model_dump()

        for key in data:
            self.__add_section_title(key)
            if 'readme' in data[key]:
                self.__add_section_title('Readme summary')
                self.__add_main_text_readme(data[key])

        # Build the PDF document
        self.doc.build(self.flowables)
        print(f"PDF with formatted summary generated: {self.filename}")


    def __add_section_title(self, title):
        self.flowables.append(Paragraph(title, self.styles['Heading1']))
        self.flowables.append(Spacer(1, 12))

    def __add_main_text_readme(self, readme_text):
        formatted_summary = ''

        # Split the summary text into lines
        lines = readme_text['summary'].split('\n')

        for line in lines:
            # Check for code segments enclosed in backticks and apply code style
            line = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', line)

            # Check if the line starts with a hashtag and should be bold
            if line.startswith('#'):
                # Remove the '#' and strip leading whitespace, then wrap with bold tags
                line = line.lstrip('# ').strip()
                line = f'<b>{line}</b>'

            formatted_summary += line + '<br />\n'

        # Remove the last line break
        formatted_summary = formatted_summary.rstrip('<br />\n')

        # Append the formatted summary to the flowables
        self.flowables.append(Paragraph(formatted_summary, self.text_style))
        self.flowables.append(Spacer(1, 12))
        self.flowables.append(PageBreak())

    