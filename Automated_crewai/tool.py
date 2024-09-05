import markdown
from xhtml2pdf import pisa
import os
from crewai_tools import tool
import fitz  # PyMuPDF
from markdownify import markdownify as md
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

@tool
def markdown_to_pdf(input_file_name: str, output_file_name: str) -> str:
    """
    Convert a Markdown file to a PDF and save it as a .pdf file while retaining the Markdown formatting.

    Args:
    input_file_name (str): The name of the Markdown file to be converted.
    output_file_name (str): The name of the PDF file where the output will be saved.

    Returns:
    str: A message indicating the success or failure of the operation.
    """
    try:
        if not os.path.isfile(input_file_name):
            return f"Error: File '{input_file_name}' not found."

        with open(input_file_name, 'r', encoding='utf-8') as md_file:
            md_content = md_file.read()

        html_content = markdown.markdown(md_content)

        with open(output_file_name, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

        return f"Successfully converted {input_file_name} to {output_file_name}" if not pisa_status.err else f"Failed to convert {input_file_name} to {output_file_name}"

    except Exception as e:
        return f"An error occurred: {e}"

@tool
def pdf_to_markdown(input_file: str, output_file: str = "final_jd.md") -> str:
    """
    Convert a PDF file to a Markdown file and save it as a .md file.

    Args:
    input_file (str): The name of the PDF file to be converted.
    output_file (str): The name of the Markdown file where the output will be saved. Defaults to "final_jd.md".

    Returns:
    str: A message indicating the success or failure of the operation.
    

    """
    try:
        if not os.path.isfile(input_file):
            return f"Error: File '{input_file}' not found."

        pdf_document = fitz.open(input_file)
        text = ""

        for page in pdf_document:
            text += page.get_text("text") + "\n\n"

        markdown_content = md(text, heading_style="ATX")

        with open(output_file, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)

        return f"Successfully converted {input_file} to {output_file}"

    except Exception as e:
        return f"An error occurred: {e}"

class LinkedInPoster:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def linkedin_login(self):
        """Login to LinkedIn."""
        self.driver.get("https://www.linkedin.com/login")
        self.driver.maximize_window()

        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(
                By.XPATH, "//button[@type='submit']"
            )

            email_field.send_keys(self.email)
            password_field.send_keys(self.password)
            login_button.click()

            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//a[@href='/feed/']"))
            )
            print("Login successful")
        except Exception as e:
            print(f"Login failed: {e}")

    def clean_content(self, content: str) -> str:
        """
        Remove Markdown formatting symbols from content.

        Args:
        content (str): The raw content from the file.

        Returns:
        str: The cleaned content.
        """
        # Remove Markdown headers
        content = re.sub(r"^#+\s*", "", content, flags=re.MULTILINE)
        # Remove Markdown emphasis (bold, italic, etc.)
        content = re.sub(r"(\*\*|__|\*|_)+", "", content)
        # Remove Markdown links
        content = re.sub(r"!\[.*?\]\(.*?\)", "", content)
        content = re.sub(r"\[.*?\]\(.*?\)", "", content)
        # Remove Markdown code blocks
        content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        content = re.sub(r"`.*?`", "", content)
        # Remove unnecessary whitespace
        content = re.sub(r"\n\s*\n", "\n\n", content)
        return content.strip()

    def post_to_linkedin(self, file_path: str = "job_skills.md"):
        """Post the content of the file to LinkedIn."""
        self.linkedin_login()
        time.sleep(4)  # Allow time for login to complete

        try:
            self.driver.get("https://www.linkedin.com/feed/")

            # Wait for and click the share box
            share_box = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(@class,'share-box-feed-entry__trigger')]",
                    )
                )
            )
            share_box.click()
            print("Share box clicked.")

            # Handle potential overlays or modals
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located(
                        (By.CSS_SELECTOR, "div.artdeco-modal__content")
                    )
                )
            except Exception as e:
                print(f"No overlay found or could not wait for it to disappear: {e}")

            # Wait for the post text area to be interactable
            post_text_area = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
            )
            print("Post text area is visible.")

            # Scroll the post text area into view
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", post_text_area
            )
            time.sleep(1)  # Short pause to ensure it's fully visible

            # Ensure the element is interactable by clicking or focusing it
            post_text_area.click()

            # Read the post content from the file
            with open(file_path, "r") as file:
                post_content = file.read()
                print(f"Post content read from file:\n{post_content[:6000]}")

            # Clean the post content by removing Markdown formatting
            clean_post_content = self.clean_content(post_content)

            # Simulate typing the content into the textbox
            post_text_area.send_keys(clean_post_content)
            print("Post content entered.")

            # Wait for the post button to be clickable
            post_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(@class,'share-actions__primary-action')]",
                    )
                )
            )
            # Scroll the post button into view to ensure it is visible
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", post_button
            )
            time.sleep(1)  # Short pause to ensure it's fully visible

            post_button.click()
            print("Post button clicked.")
            print("Post submitted successfully")

        except Exception as e:
            print(f"An error occurred: {e}")
            self.driver.save_screenshot("screenshot.png")
        finally:
            time.sleep(4)  # Allow time for the post to be processed
            self.driver.quit()


@tool
def linkedin_post(email: str, password: str):
    """
    Login to LinkedIn and post the content of a default file.

    Args:
    email (str): LinkedIn login email address.
    password (str): LinkedIn login password.
   
    """
    poster = LinkedInPoster(email, password)
    poster.post_to_linkedin()
    print("LinkedIn post process completed.")


# @tool
# def linkedin_post(email: str, password: str, file_path: str = r"C:\Users\HP\Documents\miniollam\Automated_crewai\final_jd.md"):
#     """
#     Login to LinkedIn and post the content of a file (Markdown or converted PDF content).

#     Args:
#     email (str): LinkedIn login email address.
#     password (str): LinkedIn login password.
#     file_path (str): Path to the file to be posted (Markdown or other text-based file).
#     """
#     service = Service(ChromeDriverManager().install())
#     options = webdriver.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--start-maximized")
    
#     driver = webdriver.Chrome(service=service, options=options)
#     poster = LinkedInPoster(email, password, driver)
#     poster.post_to_linkedin(file_path)
#     print("Posted to LinkedIn successfully!")


# import markdown
# from xhtml2pdf import pisa
# import os
# from crewai_tools import tool


# @tool
# def markdown_to_pdf(input_file_name: str, output_file_name: str) -> str:
#     """
#     Convert a Markdown file to a PDF and save it as a .pdf file while retaining the Markdown formatting.

#     Args:
#     input_file_name (str): The name of the Markdown file to be converted.
#     output_file_name (str): The name of the PDF file where the output will be saved.

#     Returns:
#     str: A message indicating the success or failure of the operation.
#     """
#     try:
#         # Check if the input file exists
#         if not os.path.isfile(input_file_name):
#             return f"Error: File '{input_file_name}' not found."

#         # Read Markdown file
#         with open(input_file_name, "r", encoding="utf-8") as md_file:
#             md_content = md_file.read()

#         # Convert Markdown to HTML
#         html_content = markdown.markdown(md_content)

#         # Convert HTML to PDF
#         with open(output_file_name, "wb") as pdf_file:
#             pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

#         if pisa_status.err:
#             return f"Failed to convert {input_file_name} to {output_file_name}"
#         else:
#             return f"Successfully converted {input_file_name} to {output_file_name}"

#     except Exception as e:
#         return f"An error occurred: {e}"


# import fitz  # PyMuPDF
# from markdownify import markdownify as md
# import os
# from crewai_tools import tool


# @tool
# def pdf_to_markdown(input_file: str, output_file: str = "final_jd.md") -> str:
#     """
#     Convert a PDF file to a Markdown file and save it as a .md file.

#     Args:
#     input_file (str): The name of the PDF file to be converted.
#     output_file (str, optional): The name of the Markdown file where the output will be saved. Defaults to 'final_jd.md'.

#     Returns:
#     str: A message indicating the success or failure of the operation.
#     """
#     try:
#         # Check if the input file exists
#         if not os.path.isfile(input_file):
#             return f"Error: File '{input_file}' not found."

#         # Open the PDF file
#         pdf_document = fitz.open(input_file)
#         text = ""

#         # Extract text from each page
#         for page_num in range(len(pdf_document)):
#             page = pdf_document.load_page(page_num)
#             text += page.get_text("text") + "\n\n"

#         # Convert the text to Markdown
#         markdown_content = md(text, heading_style="ATX")

#         # Save the Markdown content to the output file
#         with open(output_file, "w", encoding="utf-8") as md_file:
#             md_file.write(markdown_content)

#         return f"Successfully converted {input_file} to {output_file}"

#     except Exception as e:
#         return f"An error occurred: {e}"


# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# import time
# import re
# from crewai_tools import tool


# class LinkedInPoster:
#     def __init__(self, email: str, password: str):
#         self.email = email
#         self.password = password
#         self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

#     def linkedin_login(self):
#         """Login to LinkedIn."""
#         self.driver.get("https://www.linkedin.com/login")
#         self.driver.maximize_window()

#         try:
#             WebDriverWait(self.driver, 15).until(
#                 EC.presence_of_element_located((By.ID, "username"))
#             )
#             email_field = self.driver.find_element(By.ID, "username")
#             password_field = self.driver.find_element(By.ID, "password")
#             login_button = self.driver.find_element(
#                 By.XPATH, "//button[@type='submit']"
#             )

#             email_field.send_keys(self.email)
#             password_field.send_keys(self.password)
#             login_button.click()

#             WebDriverWait(self.driver, 15).until(
#                 EC.presence_of_element_located((By.XPATH, "//a[@href='/feed/']"))
#             )
#             print("Login successful")
#         except Exception as e:
#             print(f"Login failed: {e}")

#     def clean_content(self, content: str) -> str:
#         """
#         Remove Markdown formatting symbols from content.

#         Args:
#         content (str): The raw content from the file.

#         Returns:
#         str: The cleaned content.
#         """
#         # Remove Markdown headers
#         content = re.sub(r"^#+\s*", "", content, flags=re.MULTILINE)
#         # Remove Markdown emphasis (bold, italic, etc.)
#         content = re.sub(r"(\*\*|__|\*|_)+", "", content)
#         # Remove Markdown links
#         content = re.sub(r"!\[.*?\]\(.*?\)", "", content)
#         content = re.sub(r"\[.*?\]\(.*?\)", "", content)
#         # Remove Markdown code blocks
#         content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
#         content = re.sub(r"`.*?`", "", content)
#         # Remove unnecessary whitespace
#         content = re.sub(r"\n\s*\n", "\n\n", content)
#         return content.strip()

#     def post_to_linkedin(self, file_path: str = "job_skills.md"):
#         """Post the content of the file to LinkedIn."""
#         self.linkedin_login()
#         time.sleep(4)  # Allow time for login to complete

#         try:
#             self.driver.get("https://www.linkedin.com/feed/")

#             # Wait for and click the share box
#             share_box = WebDriverWait(self.driver, 30).until(
#                 EC.element_to_be_clickable(
#                     (
#                         By.XPATH,
#                         "//button[contains(@class,'share-box-feed-entry__trigger')]",
#                     )
#                 )
#             )
#             share_box.click()
#             print("Share box clicked.")

#             # Handle potential overlays or modals
#             try:
#                 WebDriverWait(self.driver, 10).until(
#                     EC.invisibility_of_element_located(
#                         (By.CSS_SELECTOR, "div.artdeco-modal__content")
#                     )
#                 )
#             except Exception as e:
#                 print(f"No overlay found or could not wait for it to disappear: {e}")

#             # Wait for the post text area to be interactable
#             post_text_area = WebDriverWait(self.driver, 30).until(
#                 EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
#             )
#             print("Post text area is visible.")

#             # Scroll the post text area into view
#             self.driver.execute_script(
#                 "arguments[0].scrollIntoView(true);", post_text_area
#             )
#             time.sleep(1)  # Short pause to ensure it's fully visible

#             # Ensure the element is interactable by clicking or focusing it
#             post_text_area.click()

#             # Read the post content from the file
#             with open(file_path, "r") as file:
#                 post_content = file.read()
#                 print(f"Post content read from file:\n{post_content[:6000]}")

#             # Clean the post content by removing Markdown formatting
#             clean_post_content = self.clean_content(post_content)

#             # Simulate typing the content into the textbox
#             post_text_area.send_keys(clean_post_content)
#             print("Post content entered.")

#             # Wait for the post button to be clickable
#             post_button = WebDriverWait(self.driver, 30).until(
#                 EC.element_to_be_clickable(
#                     (
#                         By.XPATH,
#                         "//button[contains(@class,'share-actions__primary-action')]",
#                     )
#                 )
#             )
#             # Scroll the post button into view to ensure it is visible
#             self.driver.execute_script(
#                 "arguments[0].scrollIntoView(true);", post_button
#             )
#             time.sleep(1)  # Short pause to ensure it's fully visible

#             post_button.click()
#             print("Post button clicked.")
#             print("Post submitted successfully")

#         except Exception as e:
#             print(f"An error occurred: {e}")
#             self.driver.save_screenshot("screenshot.png")
#         finally:
#             time.sleep(4)  # Allow time for the post to be processed
#             self.driver.quit()


# @tool
# def linkedin_post(email: str, password: str):
#     """
#     Login to LinkedIn and post the content of a default file.

#     Args:
#     email (str): LinkedIn login email address.
#     password (str): LinkedIn login password.
#     """
#     poster = LinkedInPoster(email, password)
#     poster.post_to_linkedin()
#     print("LinkedIn post process completed.")
