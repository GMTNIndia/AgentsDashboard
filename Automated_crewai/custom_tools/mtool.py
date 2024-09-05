from crewai_tools import Tool, tool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from crewai_tools import tool

@tool
def SeleniumScrapingTool(markdown_file_path: str) -> str:
    """
    A tool that uses Selenium to upload Markdown file content to the Markmap website and render the mindmap.

    Args:
        markdown_file_path (str): The path to the Markdown file to be processed.

    Returns:
        str: A message indicating the result of the operation.
    """
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("detach", True)  # Keep the browser open

    # Set up WebDriver
    service = Service(executable_path=r"C:\mainmap\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Read the Markdown file
        with open(markdown_file_path, "r") as file:
            markdown_text = file.read()

            time.sleep(3)
            driver.get(
                r"C:\Users\HP\Documents\miniollam\Automated_crewai"
            )

            markdown_element = driver.find_element(By.TAG_NAME, "body")
            time.sleep(5)
            markdown_element.send_keys(Keys.CONTROL + "a")
            markdown_element.send_keys(Keys.CONTROL + "c")
            time.sleep(5)

        # Navigate to Markmap website
        driver.get("https://markmap.js.org/repl")

        # Wait for the CodeMirror element to be present
        wait = WebDriverWait(driver, 10)
        code_mirror_element = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div[2]/div[1]/div/div[2]/div[2]")))

        # Clear existing content and paste new content
        code_mirror_element.click()
        code_mirror_element.send_keys(Keys.CONTROL + "a")
        code_mirror_element.send_keys(Keys.DELETE)
        time.sleep(5)
        code_mirror_element.send_keys(Keys.CONTROL + "v")

        # Allow some time for the rendering
        time.sleep(5)

        # Find and click the download buttons
        download_svg = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/div[2]/div[3]/div[2]/a")))
        download_svg.click()

        download_html = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/div[2]/div[3]/div[1]/a")))
        download_html.click()

        # Allow some time for downloads to complete
        time.sleep(5)

        return "Mindmap generated and downloads initiated."
    except Exception as e:
        return f"An error occurred: {str(e)}"
    # Note: We're not quitting the driver to keep the browser open

# Example usage
# if __name__ == "__main__":
#     result = SeleniumScrapingTool(r"C:\Users\HP\Desktop\Mindmap\markmap\documents4\agent_markdown_formatter.md")
#     print(result)



