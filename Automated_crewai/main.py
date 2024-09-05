import traceback
from fastapi import FastAPI, Form, HTTPException, status, Query
from fastapi.responses import (
    HTMLResponse,
    PlainTextResponse,
    FileResponse,
    JSONResponse,
)
from fastapi.staticfiles import StaticFiles

from crewai import Crew, Process
from langchain_community.llms import Ollama

from langchain_groq import ChatGroq
from agent import Agents
from task import Tasks
import httpx
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from custom_tools.maindmap import SeleniumScrapingTool
from typing import Optional
from pymongo import MongoClient
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import markdown
import re
import os
import logging
import traceback
from custom_tools.sqlite_tool import setup_login_registration_database, register_user
from io import BytesIO
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from dotenv import load_dotenv
from crewai_tools import SerperDevTool, FileReadTool



load_dotenv()




logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

DATABASE_PATH = "users.db"

app.mount("/files", StaticFiles(directory="C:/Users/HP/Downloads"), name="files")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


agents = Agents()
tasks = Tasks()

my_llm = ChatGroq(
    api_key="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",
    model="llama3-8b-8192",
)

# my_llm = Ollama(model="phi3:latest")
# my_llm = Ollama(model="llama3-8b-8192")

mongo_client = MongoClient("mongodb://localhost:27017/")
# db = mongo_client["job_analysis"]
# collection = db["reports"]
db = mongo_client["job_database"]
collection = db["job_postings"]


driver: Optional[webdriver.Chrome] = None
# db = mongo_client["job_database"]
# collection = db["job_postings"]


def handle_exception(e: Exception):
    logger.error(f"An error occurred: {str(e)}")
    logger.error(traceback.format_exc())
    return HTTPException(status_code=500, detail=str(e))



async def process_topic(
    endpoint: str, topic: str, method: str = "GET", timeout: float = 30.0
):
    url = f"http://localhost:8080{endpoint}"

    params = {"topic": topic}

    try:
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, params=params, timeout=timeout)
            elif method.upper() == "POST":
                response = await client.post(url, data=params, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            result = response.text
            return result
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"HTTP error: {e.response.status_code} - {e.response.text}",
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Request error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing topic: {str(e)}",
        )


class LoginRegisterRequest(BaseModel):
    action: str
    email: str
    password: str
    username: str = ""
    company_name: str = ""
    topic: str = "User Authentication"


@app.post("/login-register/")
async def login_register_task_api(request: LoginRegisterRequest):
    try:
        auth_agent = agents.login_register_agent(my_llm, request.topic)

        if request.action == "register":
            auth_task = tasks.register_task(
                auth_agent,
                request.username,
                request.email,
                request.password,
                request.company_name,
            )
        elif request.action == "login":
            auth_task = tasks.login_task(auth_agent, request.email, request.password)
        else:
            raise HTTPException(
                status_code=400, detail="Invalid action. Use 'login' or 'register'."
            )

        crew = Crew(
            agents=[auth_agent],
            tasks=[auth_task],
            verbose=True,
        )

        result = crew.kickoff()

        if "Error" in result:
            raise HTTPException(status_code=400, detail=result)
        else:
            return {"message": result}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Authentication task error: {str(e)}",
        )


@app.get("/stakeholder/", response_class=HTMLResponse)
async def get_stakeholder_task_page():
    return FileResponse("outs/stakeholder.md")


@app.post("/stakeholder/")
async def stakeholder_task_api(topic: str = Form(...)):
    try:
        stakeholder_agent = agents.stakeholder_agent(my_llm, topic)
        stakeholder_task = tasks.stakeholder_task(stakeholder_agent, topic)
        
        crew = Crew(agents=[stakeholder_agent], tasks=[stakeholder_task], verbose=True)
        result = crew.kickoff()
        
     
        result_string = result.result if hasattr(result, 'result') else str(result)
        
        result_string = result_string.replace("**", "").replace("*", "")
        with open("outs/stakeholder.md", "w") as f:
            f.write(result_string)
        
        return PlainTextResponse(content=result_string)
    except Exception as e:
        raise handle_exception(e)


@app.get("/business_analyst/", response_class=HTMLResponse)
async def get_business_analyst_task_page():
    return FileResponse("outs/business_analyst.md")


@app.post("/business_analyst/")
async def business_analyst_task_api(topic: str = Form(...)):
    try:
        stakeholder_response = await process_topic("/stakeholder/", topic, method="GET")
        business_analyst_agent = agents.business_analyst_agent(my_llm, topic)
        business_analyst_task = tasks.business_analyst_task(
            business_analyst_agent, topic
        )

        crew = Crew(
            agents=[business_analyst_agent],
            tasks=[business_analyst_task],
            verbose=True,
        )

        result = crew.kickoff()

        # Extract the string content from the CrewOutput object
        if isinstance(result, str):
            result_string = result
        elif hasattr(result, 'result'):
            result_string = result.result
        else:
            result_string = str(result)

        # Now apply the replace method to the string
        result_string = result_string.replace("**", "").replace("*", "")

        with open("outs/business_analyst.md", "w") as f:
            f.write(result_string)

        return PlainTextResponse(
            content=f"\n{result_string}\n\nStakeholder Result:\n{stakeholder_response}"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Business analyst task error: {str(e)}",
        )
@app.get("/product_owner/", response_class=HTMLResponse)
async def get_product_owner_task_page():
    return FileResponse("outs/product_owner.md")


@app.post("/product_owner/")
async def product_owner_task_api(topic: str = Form(...)):
    try:
        product_owner_agent = agents.product_owner_agent(my_llm, topic)
        product_owner_task = tasks.product_owner_task(product_owner_agent, topic)

        crew = Crew(
            agents=[product_owner_agent],
            tasks=[product_owner_task],
            verbose=True,
        )

        crew_output = crew.kickoff()
        
        # Assuming CrewOutput has a method or attribute to get the result as a string
        # You might need to adjust this based on the actual structure of CrewOutput
        if hasattr(crew_output, 'result'):
            result = crew_output.result
        elif hasattr(crew_output, 'get_result'):
            result = crew_output.get_result()
        else:
            result = str(crew_output)  # Fallback to string representation

        result = result.replace("**", "").replace("*", "")

        with open("outs/product_owner.md", "w") as f:
            f.write(result)

        business_analyst_response = await process_topic("/business_analyst/", topic, method="POST")

        return PlainTextResponse(
            content=f"\n{result}\n\n  business_analyst Result:\n{business_analyst_response}"
        )

    except AttributeError as e:
        logger.error(f"AttributeError in product_owner_task_api: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CrewOutput: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error in product_owner_task_api: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Product owner task error: {str(e)}",
        )
@app.get("/scrum_master/", response_class=HTMLResponse)
async def get_scrum_master_task_page():
    return FileResponse("outs/scrum_master.md")


@app.post("/scrum_master/")
async def scrum_master_task_api(topic: str = Form(...)):
    try:
        scrum_master_agent = agents.scrum_master_agent(my_llm, topic)
        scrum_master_task = tasks.scrum_master_task(scrum_master_agent, topic)

        crew = Crew(
            agents=[scrum_master_agent],
            tasks=[scrum_master_task],
            verbose=True,
        )

        crew_output = crew.kickoff()
        
        # Handle the CrewOutput object
        if hasattr(crew_output, 'result'):
            result = crew_output.result
        elif hasattr(crew_output, 'get_result'):
            result = crew_output.get_result()
        else:
            result = str(crew_output)  # Fallback to string representation

        # Only apply replace if result is a string
        if isinstance(result, str):
            result = result.replace("**", "").replace("*", "")
        else:
            logger.warning(f"Unexpected result type: {type(result)}")

        with open("outs/scrum_master.md", "w") as f:
            f.write(str(result))  # Ensure we're writing a string

        try:
            product_owner_response = await process_topic(
                "/product_owner/", topic, method="POST"  # Changed to POST
            )
        except HTTPException as e:
            logger.error(f"Error fetching product owner response: {str(e)}")
            product_owner_response = f"Error: {e.detail}"

        return PlainTextResponse(
            content=f"\n{result}\n   \nProduct Owner Result:\n{product_owner_response}"
        )

    except AttributeError as e:
        logger.error(f"AttributeError in scrum_master_task_api: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CrewOutput: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error in scrum_master_task_api: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scrum master task error: {str(e)}",
        )

@app.post("/designer/")
async def generate_design(topic: str = Form(...)):
    try:
        try:
            scrum_master_response = await process_topic(
                "/scrum_master/", topic, method="POST"  # Changed to POST
            )
        except HTTPException as e:
            logger.error(f"Error fetching scrum master response: {str(e)}")
            scrum_master_response = f"Error: {e.detail}"

        designer_agent = agents.designer_agent(my_llm, topic)
        design_uiux_task1 = tasks.designer_task_html(designer_agent, topic)
        design_uiux_task2 = tasks.designer_task_css(
            designer_agent, topic, design_uiux_task1
        )

        crew = Crew(
            agents=[designer_agent],
            tasks=[design_uiux_task1, design_uiux_task2],
            verbose=True,
        )

        try:
            crew_output = crew.kickoff()
            logger.info(f"Crew kickoff result: {crew_output}")

            # Handle the CrewOutput object
            if hasattr(crew_output, 'result'):
                result = crew_output.result
            elif hasattr(crew_output, 'get_result'):
                result = crew_output.get_result()
            else:
                result = str(crew_output)  # Fallback to string representation

            if not result:
                raise ValueError("Empty result from crew kickoff")

        except Exception as e:
            logger.error(f"Error during crew kickoff: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error during crew kickoff: {str(e)}"
            )

        html_file_path = "outs/designer_output.html"  # Changed to relative path
        css_file_path = "outs/designer_output.css"  # Changed to relative path

        try:
            with open(html_file_path, "r") as f:
                html_content = f.read()

            with open(css_file_path, "r") as f:
                css_content = f.read()

            return {
                "result": {
                    "html_content": html_content,
                    "css_content": css_content,
                    "scrum_master_response": scrum_master_response
                }
            }
        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Design output files not found: {str(e)}"
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in generate_design: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Design generator task error: {str(e)}",
        )


@app.post("/developer/")
async def developer_task_api(topic: str = Form(...)):
    try:
        try:
            designer_response = await process_topic("/designer/", topic, method="POST")  # Changed to POST
        except HTTPException as e:
            logger.error(f"Error fetching designer response: {str(e)}")
            designer_response = f"Error: {e.detail}"

        developer_agent = agents.developer_agent(my_llm, topic)
        developer_task_backend = tasks.backend_developer_task(developer_agent, topic)

        crew = Crew(
            agents=[developer_agent],
            tasks=[developer_task_backend],
            verbose=True,
        )

        crew_output = crew.kickoff()
        
        # Handle the CrewOutput object
        if hasattr(crew_output, 'result'):
            result = crew_output.result
        elif hasattr(crew_output, 'get_result'):
            result = crew_output.get_result()
        else:
            result = str(crew_output)  # Fallback to string representation

        # Only apply replace if result is a string
        if isinstance(result, str):
            result = result.replace("**", "").replace("*", "")
        else:
            logger.warning(f"Unexpected result type: {type(result)}")

        try:
            with open("outs/backend_developer.md", "w") as file:
                file.write(str(result))
            with open("outs/backend_developer.md", "r") as file:
                backend_content = file.read()
        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}")
            backend_content = "File not found"

        response_content = (
            f"\n{backend_content}"
            f"Designer Task Result:\n{designer_response}\n\n"
        )
        return PlainTextResponse(content=response_content)

    except Exception as e:
        logger.error(f"Unexpected error in developer_task_api: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Developer task error: {str(e)}",
        )


@app.get("/tester/", response_class=HTMLResponse)
async def get_tester_task_page():
    return FileResponse("outs/tester.txt")


@app.post("/tester/")
async def tester_task_api(topic: str = Form(...)):
    try:
        try:
            developer_response = await process_topic("/developer/", topic, method="POST")
        except HTTPException as e:
            developer_response = f"Error: {e.detail}"

        tester_agent = agents.tester_agent(my_llm, topic)
        tester_task = tasks.tester_task(tester_agent, topic)

        crew = Crew(
            agents=[tester_agent],
            tasks=[tester_task],
            verbose=True,
        )

        result = crew.kickoff()
        
        # Handle the CrewOutput object
        if hasattr(result, 'result'):
            result_str = result.result
        elif hasattr(result, 'get_result'):
            result_str = result.get_result()
        else:
            result_str = str(result)  # Fallback to string representation
        
        result_str = result_str.replace("**", "").replace("*", "")
        
        with open("outs/tester.md", "w") as f:
            f.write(result_str)

        with open("outs/tester.md", "r") as file:
            tester_content = file.read()

        return PlainTextResponse(
            content=f"\n{tester_content}\nDeveloper Task Result:\n{developer_response}"
        )

    except Exception as e:
        logger.error(f"Unexpected error in tester_task_api: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Tester task error: {str(e)}"
        )
# @app.post("/mindmap_generator/")
# async def mindmap_generator_task_api(
#     project: str = Form(...), subtopics: Optional[str] = Form("")
# ):
#     try:
#         subtopics_list = (
#             [topic.strip() for topic in subtopics.split(",")] if subtopics else []
#         )

#         workflow_maker_agent = agents.workflow_maker_agent(my_llm, project)
#         workflow_maker_task_format = tasks.workflow_maker_task_format(
#             workflow_maker_agent, project, subtopics_list
#         )
#         mindmap_generator_task = tasks.mindmap_generator_task(
#             workflow_maker_agent, project, subtopics_list
#         )

#         crew = Crew(
#             agents=[workflow_maker_agent],
#             tasks=[workflow_maker_task_format, mindmap_generator_task],
#             verbose=True,
#         )

#         result = crew.kickoff()

#         mindmap_file_path = "C:/Users/HP/Downloads/markmap.html"
#         if os.path.exists(mindmap_file_path):
#             return {"result": "/files/markmap.html"}
#         else:
#             raise FileNotFoundError("Mindmap file not found")
#     except Exception as e:
#         print(f"Error in mindmap_generator_task_api: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Mindmap generator task error: {str(e)}",
#         )


# @app.post("/mindmap/")
# async def mindmap_api(topic: str = Form(...), subtopics: Optional[str] = Form("")):
#     try:
#         subtopics_list = (
#             [topic.strip() for topic in subtopics.split(",")] if subtopics else []
#         )

#         # Initialize agents and tasks
#         Mindmap_Creator = agents.Mindmap_Creator(my_llm, topic)
#         mindmap_format = tasks.mindmap_format(Mindmap_Creator, topic, subtopics_list)
#         mindmap_task = tasks.mindmap_task(Mindmap_Creator, topic, subtopics_list)

#         crew = Crew(
#             agents=[Mindmap_Creator],
#             tasks=[mindmap_format, mindmap_task],
#             verbose=True,
#         )

#         result = crew.kickoff()

#         mindmap_file_path = "C:/Users/HP/Downloads/markmap.html"
#         if os.path.exists(mindmap_file_path):
#             return {"result": "/files/markmap.html"}
#         else:
#             raise FileNotFoundError("Mindmap file not found")
#     except Exception as e:
#         print(f"Error in mindmap_generator_task_api: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Mindmap generator task error: {str(e)}",
#         )


@app.post("/mindmap_generator/")
async def mindmap_generator_task_api(project: str = Form(...), subtopics: Optional[str] = Form("")):
    try:
        subtopics_list = [topic.strip() for topic in subtopics.split(",")] if subtopics else []

        workflow_maker_agent = agents.workflow_maker_agent(my_llm, project)
        workflow_maker_task_format = tasks.workflow_maker_task_format(
            workflow_maker_agent, project, subtopics_list
        )
        mindmap_generator_task = tasks.mindmap_generator_task(
            workflow_maker_agent, project, subtopics_list
        )

        crew = Crew(
            agents=[workflow_maker_agent],
            tasks=[workflow_maker_task_format, mindmap_generator_task],
            verbose=True,
        )

        result = crew.kickoff()

        mindmap_file_path = "C:/Users/HP/Downloads/markmap.html"
        if os.path.exists(mindmap_file_path):
            return {"result": "/files/markmap.html"}
        else:
            raise FileNotFoundError("Mindmap file not found")
    except Exception as e:
        print(f"Error in mindmap_generator_task_api: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mindmap generator task error: {str(e)}",
        )

@app.post("/mindmap/")
async def mindmap_api(topic: str = Form(...), subtopics: Optional[str] = Form("")):
    try:
        subtopics_list = [topic.strip() for topic in subtopics.split(",")] if subtopics else []

        # Initialize agents and tasks
        Mindmap_Creator = agents.Mindmap_Creator(my_llm, topic)
        mindmap_format = tasks.mindmap_format(Mindmap_Creator, topic, subtopics_list)
        mindmap_task = tasks.mindmap_task(Mindmap_Creator, topic, subtopics_list)

        crew = Crew(
            agents=[Mindmap_Creator],
            tasks=[mindmap_format, mindmap_task],
            verbose=True,
        )

        result = crew.kickoff()

        mindmap_file_path = "C:/Users/HP/Downloads/markmap.html"
        if os.path.exists(mindmap_file_path):
            return {"result": "/files/markmap.html"}
        else:
            raise FileNotFoundError("Mindmap file not found")
    except Exception as e:
        print(f"Error in mindmap_api: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mindmap generator task error: {str(e)}",
        )


@app.get("/generate_report/")
async def generate_report(
    company_name: str = Query(..., description="Name of the company"),
    industry: str = Query(..., description="Industry of the company"),
):
    if not company_name or not industry:
        raise HTTPException(
            status_code=422, detail="Both company_name and industry must be provided."
        )

    competitive_analyst_agent = agents.competitive_analyst_agent(my_llm, company_name, industry)
    formatter_agent = agents.formatter_agent(my_llm, company_name)

    company_analysis_task = tasks.company_analysis_task(competitive_analyst_agent, company_name, industry)
    formatting_task = tasks.formatting_task(formatter_agent, company_name)

    # Define crew
    crew = Crew(
        agents=[competitive_analyst_agent, formatter_agent],
        tasks=[company_analysis_task, formatting_task],
        verbose=True,
    )

    # Kickoff crew tasks
    try:
        result = crew.kickoff()

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error during crew kickoff: {str(e)}"
        )

    output_file_path = "outs/competitors_analysis_report.md"
    if not os.path.exists(output_file_path):
        raise HTTPException(
            status_code=500, detail="Report generation failed. Output file not found."
        )

    try:
        with open(output_file_path, "r") as result:
            report_content = result.read()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading report file: {str(e)}"
        )

    formatted_report_content = report_content.replace("**", "").replace("*", "")

    return PlainTextResponse(content=formatted_report_content)


class EditedContent(BaseModel):
    content: str


@app.post("/{agent}/save")
async def save_edited_content(agent: str, edited_content: EditedContent):
    agent_file = f"outs/{agent.lower().replace(' ', '_')}.md"
    with open(agent_file, "w") as f:
        f.write(edited_content.content)
    return {"message": "Content saved successfully"}


@app.get("/Job_report/", response_class=HTMLResponse)
async def Job_report(
    job_role: str = Query(..., description="The job role to analyze"),
    description: str = Query(..., description="The description of the job role"),
):
    """Generates a job skills analysis report, stores it in MongoDB, and posts it to LinkedIn."""

    if not job_role or not description:
        raise HTTPException(
            status_code=422, detail="Job role and description must be provided."
        )

    competitive_analyst_job = agents.competitive_analyst_job(
        my_llm, job_role, description
    )
    job_analysis_task = tasks.Job_analysis_task(
        competitive_analyst_job, job_role, description
    )

    crew = Crew(
        agents=[competitive_analyst_job],
        tasks=[job_analysis_task],
        verbose=True,
    )

    try:
        result = crew.kickoff()

        report_content = str(result) if isinstance(result, str) else str(result)

        report_content = report_content.replace("**", "")

        report_content = re.sub(r"\n{2,}", "\n", report_content)

        report_content = re.sub(r"(\n)(?=\w)", r"\1\n", report_content)

        print("Crew kickoff result:", report_content)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error during crew kickoff: {str(e)}"
        )

    output_file_path = "outs/job_skills_analysis_report_raw.md"
    if not os.path.isabs(output_file_path):
        output_file_path = os.path.abspath(output_file_path)

    # Store the generated report content in the output file
    try:
        with open(output_file_path, "w") as result_file:
            result_file.write(report_content)
        print(f"Report content stored in {output_file_path}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error writing report to file: {str(e)}"
        )

    if not os.path.exists(output_file_path):
        raise HTTPException(
            status_code=500, detail="Report generation failed. Output file not found."
        )

    try:
        with open(output_file_path, "r") as result_file:
            report_content = result_file.read()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading report file: {str(e)}"
        )

    try:
        report_data = {
            "job_role": job_role,
            "description": description,
            "report_content": report_content,
            "created_at": datetime.utcnow(),
        }
        collection.insert_one(report_data)
        print(f"Report stored in MongoDB for job role: {job_role}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error storing report in database: {str(e)}"
        )

    html_content = markdown.markdown(report_content)

    post_to_linkedin(output_file_path)

    return HTMLResponse(content=html_content)


def process_markdown_to_html(markdown_content: str) -> str:
    """Convert markdown content to HTML, removing ** and ## while highlighting headings with bold letters."""
    lines = markdown_content.split("\n")
    html_lines = []
    skip_next_line = False

    for i, line in enumerate(lines):
        if skip_next_line:
            skip_next_line = False
            continue

        if line.startswith("# "):
            html_lines.append(f"<h1><strong>{line[2:]}</strong></h1>")
            if i + 1 < len(lines) and lines[i + 1].strip() == "":
                skip_next_line = True
        elif line.startswith("## "):
            html_lines.append(f"<h2><strong>{line[3:]}</strong></h2>")
            if i + 1 < len(lines) and lines[i + 1].strip() == "":
                skip_next_line = True
        elif line.startswith("- "):
            html_lines.append(f"<p>{line[2:]}</p>")
        else:
            cleaned_line = line.replace("**", "")
            html_lines.append(f"<p>{cleaned_line}</p>")

    html_content = "\n".join(html_lines)

    return html_content


def linkedin_login(driver: webdriver.Chrome):
    """Login to LinkedIn."""
    driver.get("https://www.linkedin.com/login")
    driver.maximize_window()

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        email_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        email_field.send_keys("akashv0907@gmail.com")
        password_field.send_keys("Aka$h@2001@")
        login_button.click()

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/feed/']"))
        )
        print("Login successful")
    except Exception as e:
        print(f"Login failed: {e}")


def post_to_linkedin(file_path: str):
    """Post the content of the MD file to LinkedIn."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    linkedin_login(driver)
    time.sleep(4)

    try:
        driver.get("https://www.linkedin.com/feed/")

        share_box = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class,'share-box-feed-entry__trigger')]")
            )
        )
        share_box.click()

        # Handle potential overlays or modals
        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, "div.artdeco-modal__content")
                )
            )
        except Exception as e:
            print(f"No overlay found or could not wait for it to disappear: {e}")

        # Wait for the post text area to be interactable
        post_text_area = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
        )

        # Scroll the post text area into view
        driver.execute_script("arguments[0].scrollIntoView(true);", post_text_area)
        time.sleep(1)  # Short pause to ensure it's fully visible

        # Ensure the element is interactable by clicking or focusing it
        post_text_area.click()

        # Read the post content from the file
        with open(file_path, "r") as file:
            post_content = file.read()
            print(f"Post content read from file:\n{post_content[:6000]}")

        # Simulate typing the content into the textbox
        for line in post_content.split("\n"):
            post_text_area.send_keys(line)
            post_text_area.send_keys("\n")  # Adding line breaks as in markdown

        # Click the post button
        post_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class,'share-actions__primary-action')]")
            )
        )
        post_button.click()

        print("Post submitted successfully")

    except Exception as e:
        print(f"An error occurred: {e}")
        driver.save_screenshot("screenshot.png")
    finally:
        time.sleep(4)
        driver.quit()


# @app.post("/create-custom-agent/")
# async def create_custom_agent_endpoint(
#     name: str = Form(...),
#     role: str = Form(...),
#     goal: str = Form(...),
#     backstory: str = Form(...),
# ):
#     try:
#         # Create the custom agent with the new parameters
#         new_agent = agents.create_custom_agent(my_llm, name, role, goal, backstory)
#         # Save the created agent
#         agents.save_agent(new_agent)
#         return {"message": f"Custom  '{name}' created successfully"}
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Error creating custom agent: {str(e)}"
#         )


@app.post("/create-custom-agent/")
async def create_custom_agent_endpoint(
    name: str = Form(...),
    role: str = Form(...),
    goal: str = Form(...),
    backstory: str = Form(...),
    llm_type: str = Form(...),
    model_name: str = Form(...),
    api_key: Optional[str] = Form(None)
):
    try:
        # Create the custom agent with the new parameters
        new_agent = agents.create_custom_agent(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            llm_type=llm_type,
            model_name=model_name,
            api_key=api_key
        )
        
        # Save the created agent
        agents.save_agent(new_agent)
        
        return {"message": f"Custom agent '{name}' created successfully"}
    except ValueError as ve:
        # This will catch the specific ValueError we raised for unsupported LLM types
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # This will catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"Error creating custom agent: {str(e)}")
@app.get("/get-available-models/")
async def get_available_models():
    return agents.get_available_models()

@app.post("/create-custom-task/")
async def create_custom_task(
    agent_name: str = Form(...),
    task_description: str = Form(...),
    expected_output: str = Form(...),
    output_file: str = Form(...),
    tool_name: str = Form(...),          
    api_key: Optional[str] = Form(None),  # Optional, only required for specific tools
):
    try:
        custom_agent = agents.get_agent_by_name(agent_name)
        if not custom_agent:
            raise HTTPException(
                status_code=404, detail=f"Agent '{agent_name}' not found"
            )

        # Initialize tool configuration
        tools = None

        if tool_name == "SerperTool":
            os.environ["SERPER_API_KEY"] = api_key
            tools = [SerperDevTool()]  # Ensure SerperDevTool is a proper subclass with _run method
        elif tool_name == "FileReadTool":
            tools = [FileReadTool()]  # Ensure FileReadTool is a proper subclass with _run method
        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown tool '{tool_name}'"
            )

        # Check if tools are properly instantiated
        if not all(hasattr(tool, '_run') and callable(getattr(tool, '_run')) for tool in tools):
            raise HTTPException(
                status_code=400, detail="One or more tools are missing the required '_run' method implementation"
            )

        # Create the custom task with the selected tool
        new_task = tasks.create_custom_task(
            custom_agent, task_description, expected_output, output_file, tools
        )

        return {"message": f"Custom task for '{agent_name}' created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating custom task: {str(e)}"
        )


@app.post("/execute-custom-task/")
async def execute_custom_task(
    agent_name: str = Form(...), task_description: str = Form(...)
):
    try:
        custom_agent = agents.get_agent_by_name(agent_name)
        if not custom_agent:
            raise HTTPException(
                status_code=404, detail=f"Agent '{agent_name}' not found"
            )

        custom_task = tasks.get_task_by_description(task_description)
        if not custom_task:
            raise HTTPException(
                status_code=404, detail=f"Task '{task_description}' not found"
            )

        crew = Crew(
            agents=[custom_agent],
            tasks=[custom_task],
            verbose=True,
        )

        result = crew.kickoff()
        
        # Handle the CrewOutput object
        if hasattr(result, 'result'):
            result_str = result.result
        elif hasattr(result, 'get_result'):
            result_str = result.get_result()
        else:
            result_str = str(result)  # Fallback to string representation

        return JSONResponse(content={"result": result_str})
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in execute_custom_task: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error executing custom task: {str(e)}"
        )






@app.get("/execute_crew_tasks/")
async def execute_crew_tasks(
    Position: str,
    Number_of_Openings: int,
    Experience_Level: str,
    Branch: str,
    Location: str,
    Primary_Skills: str,
    Desired_Skills: str,
    Certifications: str,
    Job_Description: str,
):
    current_time = datetime.now()
    job_data = {
        "Position": Position,
        "Number_of_Openings": Number_of_Openings,
        "Experience_Level": Experience_Level,
        "Branch": Branch,
        "Location": Location,
        "Primary_Skills": Primary_Skills,
        "Desired_Skills": Desired_Skills,
        "Certifications": Certifications,
        "Job_Description": Job_Description,
        "Created_At": current_time,
    }

    # Save job data to MongoDB
    collection.insert_one(job_data)

    # Create and run the Crew tasks for JD
    hiring_manager = agents.hiring_manager(my_llm)
    JD_task = tasks.JD_task(
        hiring_manager,
        Position,
        Number_of_Openings,
        Experience_Level,
        Branch,
        Location,
        Primary_Skills,
        Desired_Skills,
        Certifications,
        Job_Description,
    )
    converter_task = tasks.converter_task(
        hiring_manager, "job_description.md", "job_description.pdf"
    )

    crew = Crew(
        agents=[hiring_manager],
        tasks=[JD_task, converter_task],
        verbose=True,
    )
    project_result1 = crew.kickoff()

    # Read the content of job_description.md
    with open("job_description.md", "r") as file:
        job_description_content = file.read()

    result = {
      
       
        "job_description_content": job_description_content
    }

    return JSONResponse(content=result)



@app.get("/execute_additional_tasks/")
async def execute_additional_tasks(input_file: str, email: str, password: str):
    competitive_analyst = agents.competitive_analyst(my_llm)
    pdf_to_md_converter_task = tasks.pdf_to_md_converter_task(competitive_analyst, input_file)
    analysis_task = tasks.analysis_task(competitive_analyst)
    linkedin_post_task = tasks.linkedin_post_task(competitive_analyst, email, password)

    crew = Crew(
        agents=[competitive_analyst],
        tasks=[pdf_to_md_converter_task, analysis_task, linkedin_post_task],
        verbose=True,
    )
    project_result2 = crew.kickoff()

    # Read the content of job_skills.md
    with open("job_skills.md", "r") as file:
        job_skills_content = file.read()

    result = {
       
        "job_skills_content": job_skills_content
    }

    return JSONResponse(content=result)




class ResultUpdate(BaseModel):
    result: str


@app.post("/update-result/")
async def update_result(result: ResultUpdate):
    try:
        # Here you would typically update the result in your database or storage system
        # For this example, we'll just return a success message
        return JSONResponse(content={"message": "Result updated successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating result: {str(e)}")


@app.post("/digital_marketing_agent/")
async def create_post(topic: str = Form(...)):
    try:
     
        seo_specialist = agents.seo_specialist(my_llm, topic)
        researcher = agents.researcher(my_llm, topic)
        company_blog_writer = agents.Company_Blog_Writer(my_llm, topic)

       
        seo_task = tasks.seo_task(seo_specialist, topic)
        research_task = tasks.research_task(researcher, topic, [seo_task])
        blog_writer_task = tasks.Company_Blog_Writer_Task(company_blog_writer, topic, [research_task])

       
        crew = Crew(
            agents=[seo_specialist, researcher, company_blog_writer],
            tasks=[seo_task, research_task, blog_writer_task],
            verbose=True,
        )

    
        result = crew.kickoff()

        result_string = result.result if hasattr(result, 'result') else str(result)

       
        result_string = result_string.replace("**", "").replace("*", "")

        
        with open("outs/content.md", "w") as f:
            f.write(result_string)

        
        return PlainTextResponse(content=result_string)
    except Exception as e:
        raise handle_exception(e)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)

file_path = r"C:\Users\HP\Desktop\mini\mini\Automated_crewai\outs\job_skills_analysis_report_raw.md"

