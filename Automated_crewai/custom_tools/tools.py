import re
from crewai_tools import tool


@tool
def read_content(file_path):
    """
    Read content to the specified file path.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


@tool
def write_content(file_path, content):
    """
    Write content to the specified file path.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


@tool
def clean_html(content):
    """
    Clean HTML content by removing comments, extra whitespace, and extracting
    the content within <html>...</html> tags.
    """
    
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    # Extract content within <html>...</html> tags
    match = re.search(r'(?s)<html.*?>.*?</html>', content)
    if match:
        content = match.group(0)
    else:
        content = ''  # If no <html>...</html> tags are found, result in empty content

    # Remove extra whitespace and blank lines
    content = re.sub(r'\n\s*\n', '\n', content)
    content = content.strip()

    return content

@tool
def clean_css(content):
    """
    Clean CSS content by removing everything before the first CSS rule starts
    and everything after the last CSS rule ends. Also add responsive design rules.
    """
    # Find the content between the first '{' and the last '}'
    match = re.search(r'\{.*?\}', content, flags=re.DOTALL)
    if match:
        # Extract the portion of content from the first '{' to the last '}'
        start_index = content.find('.mobile-frame {')
        end_index = content.rfind('}') + 1
        # Extract the CSS rules
        cleaned_content = content[start_index:end_index]
    else:
        # If no rules are found, return an empty string
        cleaned_content = ''

    # Remove CSS comments
    cleaned_content = re.sub(r'/\*.*?\*/', '', cleaned_content, flags=re.DOTALL)

    # Remove extra whitespace and blank lines
    cleaned_content = re.sub(r'\n\s*\n', '\n', cleaned_content)
    cleaned_content = cleaned_content.strip()

    # Add responsive design CSS
    responsive_css = '''
/* Responsive Design */
@media only screen and (min-width: 768px) {
  .mobile-frame {
    width: 360px;
    height: 640px;
    border: none;
    box-shadow: none;
  }
}
    '''
    final_css = f"{cleaned_content}\n\n{responsive_css}"
    
    return final_css


@tool
def main():
    """
    Main function to read, clean, and write HTML and CSS files.
    """
    # Paths for HTML and CSS files
    html_input_file_path = 'outs/designer_output.html'
    html_output_file_path = 'outs/designer_output.html'
    css_input_file_path = 'outs/designer_output.css'
    css_output_file_path = 'outs/designer_output.css'

    # Clean HTML content
    html_content = read_content(html_input_file_path)
    cleaned_html_content = clean_html(html_content)
    write_content(html_output_file_path, cleaned_html_content)
    print(f"Cleaned HTML content has been written to '{html_output_file_path}'.")

    # Clean CSS content
    css_content = read_content(css_input_file_path)
    cleaned_css_content = clean_css(css_content)
    write_content(css_output_file_path, cleaned_css_content)
    print(f"Cleaned CSS content has been written to '{css_output_file_path}'.")

if __name__ == "__main__":
    main()
