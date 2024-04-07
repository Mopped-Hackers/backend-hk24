from ...models import DataStory
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import json
import re


class PdfGenerator:
    def __init__(self,app:FastAPI, story: DataStory) -> None:

        root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        uploads_folder = os.path.join(root_path, 'uploads')
        if not os.path.exists(uploads_folder):
            os.makedirs(uploads_folder)
        app.mount("/static", StaticFiles(directory=uploads_folder), name="static")

        storyUrl = story.url.replace("https://", "").replace("http://", "").replace("/", "_")
        
        self.filename = os.path.join(uploads_folder,f"./structured_output_{storyUrl}_{story.id}.pdf")
        self.story: DataStory = story


        self.doc = SimpleDocTemplate(self.filename, pagesize=letter)
        styles = getSampleStyleSheet()
        self.text_style = styles['Normal']
        self.code_style = ParagraphStyle(
            'Code',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=10,
            leading=12,
            textColor=colors.black,
            backColor=colors.white,
            leftIndent=20
        )

        self.flowables = []
        self.code_indent_style = ParagraphStyle('CodeIndent', parent=styles['Normal'], fontName='Courier', leftIndent=20)
        self.docstring_style = ParagraphStyle(
            'Docstring',
            parent=styles['Normal'],
            textColor=colors.green,
            leftIndent=20,
        )
        self.styles = getSampleStyleSheet()  


        
    def add_section_title(self,title):
        self.flowables.append(Paragraph(title, self.styles['Heading1']))
        self.flowables.append(Spacer(1, 12))


    def add_main_text_readme(self,readme_text):
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


    def add_business_story(self,story):
        self.flowables.append(Paragraph(story['name'], self.styles['Heading2']))

        for section in story['story']:
            route = section['route']
            functions = section['functions']
            order_summary = section['order_summary']
            _story = section['story']

            # Add the route to the flowables
            self.flowables.append(Paragraph(f'<b>Route:</b> {route}', self.text_style))

            # Check if there are any functions and format them with indentation
            if functions:
                self.flowables.append(Paragraph('<b>Functions:</b>', self.text_style))
                # Apply the indented style for each function
                for function in functions:
                    self.flowables.append(Paragraph(f'• <font name="Courier">{function}</font>', self.code_indent_style))
            else:
                self.flowables.append(Paragraph('<b>Functions:</b> No functions', self.text_style))

            self.flowables.append(Spacer(1, 12))

            if len(order_summary) > 0:
                lines = _story.split('\n')
                formatted_summary = ''
                for line in range(len(lines)):
                    if line == 0:
                        formatted_summary += f'<b>Case:</b><br />\n'
                    line = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', lines[line])
                    formatted_summary += line + '<br />\n'
                self.flowables.append(Paragraph(formatted_summary, self.text_style))


    def add_class_data(self,class_data):
        formatted_summary = ''

        # Format the class data, handling line breaks and code formatting
        if class_data:
            lines = class_data.split('\n')
            for line in lines:
                # Format code within backticks using <font> tags
                line = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', line)
                formatted_summary += line + '<br />\n'

        # Remove the last <br />\n since it's added by the loop
        formatted_summary = formatted_summary.rstrip('<br />\n')

        # Add the formatted summary to the flowables
        self.flowables.append(Paragraph(formatted_summary, self.styles['Normal']))
        self.flowables.append(Spacer(1, 12))


    def replace_html_entities(self,text):
        """Replace HTML entities."""
        html_entities = {
            "&amp;": "&",
            "&gt;": ">",
            "&lt;": "<",
            "&quot;": '"',
            "&#39;": "'"
        }
        for entity, char in html_entities.items():
            text = text.replace(entity, char)
        return text


    def format_class_comment(self,text):
        # Define custom style for code blocks
        code_style = ParagraphStyle(
            'Code',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=10,
            leading=12,
            textColor=colors.black,
            backColor=colors.white,
            leftIndent=20
        )

        name = text['name']
        self.flowables.append(Paragraph(f'<b>{name}</b>', self.styles['Heading2']))

        content = text['content']
        lines = content.split('\n')
        formatted_summary = self.code_section(lines)

        self.flowables.append(Paragraph(formatted_summary, code_style))
        self.flowables.append(Spacer(1, 12))


    def code_section(self,lines):
        in_docstring = False
        formatted_summary = ''
        for line in lines:
            if line.strip().startswith('"""'):
                in_docstring = not in_docstring
                line = f'<font style="color:green">{line}</font>'
            if in_docstring:
                line = f'<font color="green">{line}</font>'
            elif line.strip().startswith('def') or line.strip().startswith('Def'):
                line = f'<b>{line}</b>'
            elif line.strip().startswith('```'):
                line = re.sub(r'```([^`]+)```', self.format_code_and_docstrings, line)
                line = line.replace('python', '')
                line = re.sub(r'```([^`]+)```', '', line)
            elif line.strip().startswith('#'):
                line = line.replace('#', '"""')
                line = line + '"""'
                line = f'<font color="green">{line}</font>'
            formatted_summary += line + '<br />\n'

        return formatted_summary


    def format_code_and_docstrings(self,match):
        """Format code blocks."""
        code_block = match.group(0)
        return f'<font name="Courier">{self.replace_html_entities(code_block)}</font>'


    def add_function(self,function):
        # break the function into lines
        name = function['name']
        summary = function['summary']
        file_path = function['path']
        # take only the file name.py
        commented_code = function['code_with_comments']
        # break summary into lines
        lines = summary.split('\n')
        lines_code = commented_code.split('\n')
        # add the name of the function
        self.flowables.append(Paragraph(f'<font>{name}</font>', self.styles['Heading2']))
        self.flowables.append(Paragraph(f'<font>{file_path}</font>', self.styles['Heading4']))

        # add the summary of the function
        formatted_summary = ''
        for line in lines:
            # Check for code segments enclosed in backticks and apply code style
            line = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', line)
            formatted_summary += line + '<br />\n'
        formatted_summary = formatted_summary.rstrip('<br />\n')
        self.flowables.append(Paragraph(formatted_summary, self.text_style))
        self.flowables.append(Spacer(1, 12))

        form = self.code_section(lines_code)
        self.flowables.append(Paragraph(form, self.code_style))
        self.flowables.append(Spacer(1, 12))


    def add_function_to_test(self,key, function, test_data):
        # add the name of the function
        test_data.append(Paragraph(f'<font>{key}</font>', self.styles['Heading2']))
        for test in function:
            # line break
            lines = test.split('\n')
            # add the test name
            for line in lines:
                # Check for code segments enclosed in backticks and apply code style
                line = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', line)
                test_data.append(Paragraph(line, self.code_style))
            return test_data


    def generate_project_structure_textual(self,project_structure):

        # Function to recursively traverse the project structure dictionary and build the text tree
        def traverse_project_structure(structure, prefix=""):
            lines = []
            # Sort the items to maintain a consistent order
            items = sorted(structure.items())
            for i, (name, content) in enumerate(items):
                connector = "|--- " if i < len(items) - 1 else "|---- "
                lines.append(prefix + connector + name + "\n")  # Add a newline character
                if content:  # If the item has nested content
                    if 'dirs' in content:
                        # Recursively traverse directories
                        ext = "|   " if i < len(items) - 1 else "    "
                        lines.extend(traverse_project_structure(content['dirs'], prefix=prefix + ext))
                    if 'files' in content:
                        for file_name, functions in sorted(content['files'].items()):
                            connector = "|----" if i < len(items) - 1 else "`-- "
                            lines.append(prefix + "|   " + connector + file_name + "\n")  # Add a newline character
                            if functions:
                                for function_name in sorted(functions):
                                    lines.append(prefix + "|       |----" + function_name + "()\n")  # Add a newline character
            return lines

        # Generate the project structure as text
        return "".join(traverse_project_structure(project_structure))  # Join using empty string to utilize the newlines


    def generate_pdf(self):
        data = self.story.model_dump()
        test_data, function_data = [], []
        
        list_order = ['name', 'readme', 'business_stories', 'class_data', 'class_data_comments', 'functions']

        for key in list_order:
                if 'name' == key:
                    self.add_section_title('Name')
                    self.flowables.append(Paragraph(data[key], self.styles['Heading1']))
                    self.flowables.append(Spacer(1, 12))
                if 'readme' == key:
                    self.add_section_title('Project overview')
                    self.add_main_text_readme(data[key])
                    self.flowables.append(PageBreak())
                if 'business_stories' == key:
                    self.add_section_title('Business use cases')
                    for story in data[key]:
                        self.add_business_story(story)
                    self.flowables.append(PageBreak())
                if 'class_data' == key:
                    self.add_section_title('Dataclasses overview')
                    self.add_class_data(data[key])
                    self.flowables.append(PageBreak())
                if 'class_data_comments' == key:
                    self.add_section_title('Dataclasses')
                    for comment in data[key]:
                        self.format_class_comment(comment)
                    self.flowables.append(PageBreak())
                if 'functions' == key:
                    function_data.append(Paragraph('Functions', self.styles['Heading1']))
                    for function in data[key]:
                        self.add_function(function)
                    function_data.append(PageBreak())

        lines = self.generate_project_structure_textual(json.loads(data['project_structure']))
        self.flowables.append(Paragraph('Project structure', self.styles['Heading1']))
        for line in lines.split('\n'):
            self.flowables.append(Paragraph(line, self.text_style))

        self.doc.build(self.flowables)
