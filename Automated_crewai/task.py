from typing import Self
from crewai import Task
from textwrap import dedent
from custom_tools.maindmap import SeleniumScrapingTool
from custom_tools.tools import read_content, write_content, clean_html, clean_css, main
from custom_tools.analysis import CompetitiveAnalysisTool
from custom_tools.sqlite_tool import (
    is_valid_email,
    setup_login_registration_database,
    register_user,
    verify_email,
    authenticate_user,
)
from custom_tools.jobpost import JobSkillsAnalysisTool
from crewai_tools import FileReadTool
from crewai_tools import SerperDevTool
import os
from tool import markdown_to_pdf, pdf_to_markdown, linkedin_post


job_post = JobSkillsAnalysisTool()
analysis_tool = CompetitiveAnalysisTool()



os.environ["SERPER_API_KEY"] = "17ba5f7cdca5e20b453d8fb2a6231026ce47e345"
search_tool = SerperDevTool()


# file_read_tool = FileReadTool(
#     file_path=r"C:\Users\HP\Documents\miniollam\Automated_crewai\final_jd.md"
# )

file_read_tool = FileReadTool(file_path="final_jd.md")




class Tasks:
    def __init__(self):
        self.custom_tasks = {}
        self.tasks = []

    def stakeholder_task(self, agent, topic):

        return Task(
            description=f"Provide initial high-level requirements for {topic}.",
            expected_output="""A detailed document outlining:
                1. Introduction for the project: Overview, objectives, and the rationale behind the project.
                2. Overview of the system: High-level description of the system architecture and main components.
                3. Purpose and scope of the project: Clearly defined goals and boundaries of the project.
                4. Target audience and users: Identification of the primary users and stakeholders.
                5. High-level features and benefits: Summary of the key features and the expected benefits they will bring.
               """,
            output_file="outs/Stakeholder.md",
            
            verbose=True,
            agent=agent,
        )

    def business_analyst_task(self, agent, topic):
        return Task(
            description=f"Conduct a comprehensive business requirements analysis for {topic}.",
            expected_output="""A detailed document outlining:
                1. Executive summary: Brief overview of the business requirements analysis.
                2. Project background: Context and reasons for undertaking the project.
                3. Business objectives: Clear statement of what the business aims to achieve with this project.
                4. Stakeholder analysis: Identification and analysis of all stakeholders involved or affected by the project.
                5. Current business process: Detailed description of the current process or system (if applicable).
                6. Problem statement: Clear definition of the business problem or opportunity being addressed.
                7. Proposed solution: High-level description of the proposed solution.
                8. Functional requirements: Detailed list and description of all functional requirements.
                9. Non-functional requirements: List of all non-functional requirements (e.g., performance, security, scalability).
                10. Constraints and assumptions: Any constraints or assumptions that may impact the project.
                11. Risk analysis: Identification and assessment of potential risks and mitigation strategies.
                12. Success criteria: Clear, measurable criteria for determining project success.
                13. Glossary: Definitions of key terms and concepts used in the document.
            """,
            output_file="outs/business_analyst.md",
            agent=agent,
        )


    def product_owner_task(self, agent, topic):
        return Task(
            description=f"Create and prioritize the product backlog based on stakeholder requirements for {topic}.",
            expected_output="""A prioritized product backlog document containing:
                1. Requirement Analysis:
                    - Detailed understanding of each requirement.
                    - Well-documented requirements with user stories and acceptance criteria.
                2. Prioritization:
                    - A clear priority ranking based on stakeholder input and business value.
                    - Justification for the prioritization decisions.
                3. Refinement:
                    - Breakdown of high-level requirements into actionable tasks.
                    - Clearly defined acceptance criteria for each task.
                4. Backlog Update:
                    - Regularly updated product backlog reflecting the current state of the project.
                    - Well-groomed backlog with clearly defined priorities and tasks.
                5. Release Planning:
                    - Coordination with stakeholders to align on release timelines.
                    - Updated documentation reflecting release plans and progress.
                 """,
            output_file="outs/product_owner.md",
            agent=agent,
        )

    def scrum_master_task(self, agent, topic):
        return Task(
            description=f"Facilitate sprint planning and ensure the team adheres to Scrum practices for {topic}.",
            expected_output="""A comprehensive report on sprint planning and Scrum practices, including:
                1. Requirement Clarification:
                    - Detailed discussions and clarifications on requirements.
                    - Well-documented acceptance criteria for each user story.
                2. Documentation:
                    - Complete and clear user stories with all necessary details.
                    - Updated backlog with prioritized user stories.
                3. Prioritization:
                    - Refined backlog with prioritized tasks for the sprint.
                    - Clear criteria for prioritizing tasks.
                4. Sprint Planning:
                    - Detailed sprint planning meeting notes.
                    - Task breakdown and allocation for the sprint.
                5. Task Assignment:
                    - Clear task assignments with deadlines.
                    - Updated sprint board reflecting task assignments.
                6. Implementation:
                    - Documentation of daily stand-ups and progress updates.
                    - Notes on any impediments and resolutions.
                7. Review:
                    - Comprehensive code review reports.
                    - Feedback and suggestions for improvement.
                 """,
            output_file="outs/scrum_master.md",
            agent=agent,
        )

    def designer_task_html(self, agent, topic):
        return Task(
            description=f"""Generate a single HTML file containing mobile wireframes for a ${topic} application.""",
            expected_output=f"""
                 Create a well-structured HTML file with mobile wireframes for a ${topic} application, adhering to the following specifications:

                
                1. Structure:
                - Wrap all content in a \`<div id="designer-wireframe">\` element.
                - Create at least six \`<div class="mobile-frame">\` elements within the wrapper.
                - Each \`<div class="mobile-frame">\` should represent a different screen relevant to the ${topic} application.
                - Always include Register and Login screens.
                - The remaining screens should be specifically tailored to the ${topic}.

                2. Content:
                - Register Screen: Include fields relevant to the {topic} (e.g., username, email, password, and any topic-specific fields).
                - Login Screen: Include standard login fields and any {topic}-specific login options.
                - Home Screen (Dashboard): 
                    * Display a summary or overview specifically relevant to the {topic}.
                    * Include quick action buttons or links to main features of the {topic} application.
                    * Ensure the design is attractive and user-friendly for the specify {topic} applications.
                - Additional Screens: Create at least seven more screens specific to the {topic} functionality.

                3. Navigation:
                - Use `<header>` for the top bar with screen titles.
                - Use `<main>` for the primary content area.
                - Include `<section>` tags to group related content within each screen.
                - Utilize form elements like `<input>`, `<button>`, and `<label>` where necessary.
                
                - Include icons for home, list view, profile, and other topic-specific sections.
                
                4. Style Link:
                - Include a `<link>` tag in the `<head>` section of the HTML file to link to the external CSS file: `<link rel="stylesheet" href="designer_output.css">`.

               5. Class Names:
                - Prefix all class names with 'dw-' (for "designer wireframe") to avoid conflicts.
                - Use descriptive class names like 'dw-mobile-frame', 'dw-button', 'dw-input-field', etc.

                6. Comments:
                - Include detailed comments in the HTML explaining each section and any complex layout choices.
                - Add comments suggesting potential variations or additional features specific to the {topic}.

                The final output should be a single HTML file that, when opened in a browser and linked with the CSS file, displays a structured mobile wireframe for the {topic} application.
                """,
            output_file="outs/designer_output.html",
            # tools = [main,read_content,write_content,clean_html],
            agent=agent,
        )

    def designer_task_css(self, agent, topic, context=None):
        return Task(
            description=f"Generate a CSS file to style the HTML wireframes for a {topic} application.",
            expected_output=f"""
            Create a well-structured CSS file to style the HTML wireframes for a {topic} application, adhering to the following specifications:

            1. Scope:
            - Wrap all styles within a '#designer-wireframe' selector to isolate them from the rest of the frontend.

            2. General Styling:
            - Use the `box-sizing: border-box;` property for all elements within #designer-wireframe.
            - Reset margin and padding to zero for all elements within #designer-wireframe.

            3. App Container:
            - Style the #designer-wireframe element instead of body:
                #designer-wireframe {{
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background-color: #f4f4f4;
                    padding: 20px;
                    margin:0;
                    color:black;
                }}

            4. Mobile Frame:
            - Define a .dw-mobile-frame class with:
                .dw-mobile-frame {{
                    width: 360px;
                    height: 640px;
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    background-color: #fff;
                    margin: 10px;
                    padding: 20px;
                    
                    box-sizing: border-box;
                    overflow-y: auto;
                }}

            5. Layout Styles:
            - Style the `header` with a background color (#4CAF50), white text color, and centered text.
            - Style the `main` and `section` elements with padding and background colors. Add shadows and borders for separation.

            6. Navigation:
            - Style `.nav-menu` to be fixed at the bottom of the viewport with a background color (#4CAF50) and centered text.
            - Style navigation links with white text and include hover effects.

            7. Buttons:
            - Style `.button` with a green background, text  black, padding, border-radius, and hover effects.

            8. Form Elements:
            - Style form elements (`input`, `select`, etc.) with consistent padding, margin, border, and border-radius.

            9. Color Scheme:
            - Define CSS variables for --at-color-primary (#4CAF50) and --at-color-secondary (#ccc).

            10. Responsive Design:
            - Implement a media query for screens with a maximum width of 768px:
                @media (min-width: 768px) {{
                    #designer-wireframe .dw-mobile-frame {{
                         width: 360px;
                        height: 640px;
                        border: none;
                        box-shadow: none;
                    }}
                }}

            11. Comments:
            - Include comments in the CSS file to explain the styling choices and any complex layout decisions.

            The final CSS file should be linked to the HTML and provide a well-styled and functional mobile wireframe for the {topic} application.
            """,
            output_file="outs/designer_output.css",
            context=[context],
            # tools = [main, read_content, write_content, clean_css],
            agent=agent,
        )

    def backend_developer_task(self, agent, topic):
        return Task(
            description=f"Develop full code backend functionalities for {topic}.",
            expected_output="""Fully functional backend code including:
                1. API Endpoints:
                    - User authentication endpoints (registration, login, logout).
                    - CRUD operations for primary entities related to the project.
                    - Pagination, filtering, and sorting for data retrieval endpoints.
                2. Database Integration:
                    - Properly defined models and relationships.
                    - Use of ORM or direct database queries for data operations.
                    - Implementation of data validation and constraints.
                3. Unit and Integration Tests:
                    - Tests for each API endpoint using the project's testing framework.
                    - Mocking of external services or dependencies where applicable.
                    - Code coverage reports to ensure comprehensive test coverage.
                4. Documentation:
                    - Detailed API documentation.
                    - Setup and usage instructions for the backend system.""",
            output_file="outs/backend_developer.md",
            agent=agent,
            # human_input=True
        )

    def tester_task(self, agent, topic):
        return Task(
            description=f"Test the project to ensure it meets quality standards for {topic}.",
            expected_output="""Comprehensive test reports including and the output is  color full like Heading in one color and sub Heading in one color and add  point symbols and 
                the Heading bold output :
                1. Test Cases:
                    - Detailed test cases for functional and non-functional requirements.
                    - Coverage of all critical scenarios and edge cases.
                2. Test Execution:
                    - Execution results for each test case.
                    - List of identified bugs with detailed descriptions and steps to reproduce.
                3. Bug Reports:
                    - Prioritized list of bugs with severity and impact analysis.
                    - Recommendations for fixing the identified issues.
                4. Test Summary:
                    - Overall quality assessment of the project.
                    - Summary of testing activities and results.
                5. Regression Testing:
                    - Results of regression tests to ensure new changes do not introduce new issues.
                6. Final Quality Report:
                    - Comprehensive report summarizing all testing activities and findings.""",
            output_file="outs/tester.md",
            agent=agent,
        )

    def technical_document_task(self, agent, topic):
        return Task(
            description=f"Create a comprehensive technical documentation plan for {topic}.",
            expected_output="""A detailed document outlining:
                1. Documentation goals and objectives: Clear statement of what the documentation aims to achieve.
                2. Target audience: Identification of who will be using the documentation (e.g., developers, end-users, system administrators).
                3. Document types: List of all document types to be created (e.g., API documentation, user manuals, system architecture documents).
                4. Document structure and format: Guidelines for how each document type should be structured and formatted.
                5. Content creation and review process: Description of how content will be created, reviewed, and approved.
                6. Version control and maintenance: Plan for managing document versions and keeping documentation up-to-date.
                7. Tools and technologies: List of tools and technologies to be used in creating and managing documentation.
                8. Timeline and milestones: Proposed schedule for documentation creation and delivery.
            """,
            output_file="outs/TechnicalDocumentation.md",
            agent=agent,
        )

    def workflow_maker_task_format(self, agent, project, subtopics):
        subtopics_list = ", ".join(subtopics)

        return Task(
            description=dedent(
                f"""\
            Create a detailed workflow for the {project} that outlines all necessary steps and processes.
            Create a comprehensive and well-structured Markdown file for the mindmap for the topic: {project}.
            Don't add (```) to the markdown file.
            The workflow should include main phases, sub-tasks, and key decision points for each of the following processes:
            {subtopics_list}
            Ensure to provide a comprehensive overview of the entire project lifecycle, incorporating all these processes.
            """
            ),
            expected_output=dedent(
                f"""A detailed Markdown file with the following structure:

            # {project} Workflow

            ## 1. Project Initiation
            - Define project scope and objectives
            - Identify key stakeholders
            - Conduct initial risk assessment
            - Develop project charter

            ## 2. Planning Phase
            - Create detailed project plan
            - Define deliverables and milestones
            - Allocate resources
            - Establish communication protocols
            - Develop risk management plan

            ## 3. Execution Phase
            For each process ({subtopics_list}):
            ### [Process Name]
            - Outline specific tasks and sub-tasks
            - Assign responsibilities
            - Set timelines
            - Identify potential challenges and mitigation strategies

            ## 4. Monitoring and Controlling
            - Establish key performance indicators (KPIs)
            - Implement progress tracking mechanisms
            - Conduct regular status meetings
            - Manage changes and updates to the project plan

            ## 5. Closure and Evaluation
            - Finalize deliverables
            - Conduct project review
            - Document lessons learned
            - Obtain stakeholder sign-off
            - Archive project documents

            ## Key Decision Points
            - List critical decision points throughout the project lifecycle
            - Outline decision-making criteria and processes
            - Identify key stakeholders involved in each decision

            ## Integration Strategy
            - Describe how each process integrates with others
            - Outline dependencies between processes
            - Explain how changes in one area impact others

            ## Appendices
            - Relevant charts, diagrams, or additional resources
            - Glossary of terms
            - Reference documents

            Ensure that each section provides actionable insights and clear guidance for project execution.
            """
            ),
            output_file="outs/agent_workflow_maker.md",
            verbose=True,
            agent=agent,
        )

    def mindmap_generator_task(self, agent, topic, subtopics):
        subtopics_list = ", ".join(subtopics)
        return Task(
            description=dedent(
                f"""\
                Create a Python script that imports the SeleniumScrapingTool and uses it to process the Markdown file for the {topic}.
                The script should:
                1. Import the SeleniumScrapingTool.
                2. Set the path to the Markdown file.
                3. Call the SeleniumScrapingTool with the Markdown file path.
                4. Ensure the mindmap includes the following processes: {subtopics_list}
                """
            ),
            expected_output=dedent(
                f"""
                import SeleniumScrapingTool
                markdown_file_path = 'outs/agent_workflow_maker.md'
                SeleniumScrapingTool(markdown_file_path)
                """
            ),
            tools=[SeleniumScrapingTool],
            verbose=True,
            agent=agent,
        )

    def mindmap_format(self, agent, topic, subtopics):
        subtopics_list = ", ".join(subtopics)
        return Task(
            description=dedent(
                f"""\
                Create a comprehensive and well-structured Markdown file for the mindmap for the topic: {topic}.
                Don't add (```) to the markdown file.
                The Markdown file should include hierarchical headings and bullet points that represent the structure of the mindmap.
                Ensure to provide a detailed representation of the main concept, key ideas, and their relationships.
                """
            ),
            expected_output=dedent(
                f"""A detailed Markdown file with the following structure:
                
                # {topic} Mindmap
                ## Central Concept
                   - Main idea or topic at the center
                ## Primary Branches
                   - Key subtopics or main categories
                   - Direct connections to the central concept
                ## Secondary Branches
                   - Supporting ideas for each primary branch
                   - Details, examples, or explanations
                ## Connections and Relationships
                   - Cross-links between different branches where relevant
                ## Hierarchy and Structure
                   - Clear organization from general to specific
                   - Balanced distribution of information
                ## Visual Elements
                   - Suggested color coding for different levels or categories
                   - Potential icons or symbols to represent key concepts
                ## Additional Information
                   - Brief notes or clarifications where necessary
                   - References or sources if applicable

                Provide a textual representation of the mindmap structure, showing the hierarchy 
                and relationships between different elements. Include suggestions for visual 
                enhancements that could improve clarity and understanding of the topic.
                """
            ),
            output_file="outs/agent_workflow_maker.md",
            verbose=True,
            agent=agent,
        )

    def mindmap_task(self, agent, project, subtopics):
        subtopics_list = ", ".join(subtopics)
        return Task(
            description=dedent(
                f"""\
                Create a Python script that imports the SeleniumScrapingTool and uses it to process the Markdown file for the {project}.
                The script should:
                1. Import the SeleniumScrapingTool.
                2. Set the path to the Markdown file.
                3. Call the SeleniumScrapingTool with the Markdown file path.
                4. Ensure the mindmap includes the following processes: {subtopics_list}
                """
            ),
            expected_output=dedent(
                f"""
                import SeleniumScrapingTool
                markdown_file_path = 'outs/agent_workflow_maker.md'
                SeleniumScrapingTool(markdown_file_path)
                """
            ),
            tools=[SeleniumScrapingTool],
            verbose=True,
            agent=agent,
        )

    def company_analysis_task(self, agent, company_name, industry):
        return Task(
            description=dedent(
                f"""As a Competitive Analyst for {company_name}, operating in the {industry} industry, use the CompetitiveAnalysisTool to gather comprehensive insights and conduct a thorough analysis of the company and its competitors. Your responsibilities include:
            1. Use the tool to collect data on {company_name} and its competitors.
            2. Synthesize the collected information into a cohesive framework.
            3. Develop a detailed SWOT analysis for {company_name}.
            4. Perform a comparative analysis with its competitors.
            5. Identify key market trends, consumer preferences, and competitive positioning.
            6. Identify market cap, revenue, customer satisfaction, reviews.
            The ultimate goal is to provide actionable insights that can enhance the company's strategic decision-making and improve its competitive standing in the market."""
            ),
            agent=agent,
            expected_output=dedent(
                f"""A detailed and comprehensive analysis framework for {company_name} and its competitors that includes:
            1. Fetch top competitors for {company_name}.
            2. A thorough SWOT analysis for {company_name}.
            3. Comparative analysis with top competitors.
            4. Clear and organized visual representation of the company's market position relative to its competitors.
            5. Analysis of key metrics such as market cap, revenue, customer satisfaction, and reviews.
            6. Insights derived from the Serper search results.
            7. Actionable recommendations based on the collected data.
            8. Well-structured report with tables, charts, and other relevant visuals to effectively communicate the findings.
            9. The Serper URL used for the searches.

            Ensure all data is properly attributed and any limitations of the analysis are clearly stated."""
            ),
            tools=[analysis_tool],
            output_file="outs/competitors_analysis_report_raw.md",  # Updated path
        )

    def formatting_task(self, agent, company_name):
        return Task(
            description=dedent(
                f"""As a Report Formatter, your task is to take the raw analysis results from the competitive analysis and format them into a structured and professional report. Your responsibilities include:
            1. Organize the information into a coherent structure.
            2. Create tables, charts, and other visual aids to enhance clarity.
            3. Ensure the report is clear, concise, and professionally presented.
            4. Highlight key insights and actionable recommendations.
            5. Format the report in a way that supports strategic decision-making for {company_name}."""
            ),
            agent=agent,
            expected_output=dedent(
                f"""A professionally formatted report for {company_name} that includes:
            1. Clear and organized structure.
            2. Visual representations such as tables and charts.
            3. Highlighted insights and recommendations.
            4. A well-written document that effectively communicates the findings.
            5. The final report file 'outs/competitors_analysis_report.md'."""
            ),  # Updated path
            input_file="outs/competitors_analysis_report_raw.md",  # Updated path
            output_file="outs/competitors_analysis_report.md",  # Updated path
        )

    def register_task(self, agent, username, email, password, company_name):
        return Task(
            description=f"Register a new user with username: {username}, email: {email}, and company: {company_name}",
            expected_output=dedent(
                f"""
            A success message indicating that the user has been registered.
            If the username or email already exists, return an error message.
        """
            ),
            agent=agent,
            tools=[is_valid_email, setup_login_registration_database, register_user],
            verbose=True,
        )

    def login_task(self, agent, email, password):
        return Task(
            description=f"Authenticate user with email: {email}",
            expected_output=dedent(
                f"""
                A success message if the login is successful.
                An error message if the login fails due to incorrect password or non-existent user.
            """
            ),
            agent=agent,
            tools=[verify_email, authenticate_user],
            verbose=True,
        )

    def Job_analysis_task(self, agent, job_role, description):
        return Task(
            description=dedent(
                f"""As a Job Skills Analyst for the {job_role} role, your task is to gather and analyze data from reliable sources to understand the current market needs and trends for this position. Your responsibilities include:
                 
                1. Job Description:
                   - Use the provided description to create a refined and detailed job description that incorporates the latest trends and requirements for the {job_role} role. 
                   
                2. Key Responsibilities:
                   - Identify and list the primary responsibilities associated with the {job_role} role by reviewing job descriptions on top job portals such as LinkedIn, Indeed, and Glassdoor.
                
                3. Technical Skills:
                   - Gather information on the technical skills required for the {job_role} role, including specific programming languages, software tools, databases, and methodologies. Use industry reports and technology blogs for insights into emerging technologies.
                
                4. Non-Technical Skills:
                   - Identify the non-technical skills and soft skills essential for success in the {job_role} role, such as communication, problem-solving, and teamwork, using resources like career guides and professional forums.
                
                5. Qualifications:
                   - List the typical educational and professional qualifications required for the {job_role} role, such as degrees, certifications, or years of experience, based on industry standards and educational platforms.
                
                6. Relevant Technologies and Practices:
                   - Identify key technologies, cloud platforms, and DevOps practices that are pertinent to the {job_role} by examining industry trends and tech surveys.
                
                
                """
            ),
            agent=agent,
            expected_output=dedent(
                f"""A comprehensive and detailed analysis framework for the {job_role} role that includes:
                1. An in-depth examination of key responsibilities for the {job_role}, sourced from leading job platforms.
                2. Insights into technical skills, including programming languages, software tools, databases, and methodologies, with emphasis on emerging trends  Don't add (**) to the markdown file...
                3. Identification of non-technical skills and soft skills relevant to the {job_role}  Don't add (**) to the markdown file.. 
                4. Required qualifications, including education and certifications, corroborated by educational institutions and industry norms  Don't add (**) to the markdown file...
                5. Relevant technologies and practices, such as cloud platforms and DevOps methodologies, backed by industry reports  Don't add (**) to the markdown file...
                6. A refined job description based on the provided description and insights from job portals and industry standards  Don't add (**) to the markdown file..."""
            ),
            tools=[job_post],
            output_file="outs/job_skills_analysis_report_raw.md",
        )

    # def create_custom_task(self, agent, description, expected_output, output_file):
    #     # Create and return a new task object
    #     new_task = Task(
    #         agent=agent,
    #         description=description,
    #         expected_output=expected_output,
    #         output_file=output_file,
    #     )
    #     self.tasks.append(new_task)
    #     return new_task

    # def get_task_by_description(self, description):
    #     # Retrieve a task by its description
    #     for task in self.tasks:
    #         if task.description == description:
    #             return task
    #     return None


    def create_custom_task(self, agent, description, expected_output, output_file, tools):
    # Validate that each tool is properly implemented
     for tool in tools:
        if not hasattr(tool, '_run') or not callable(getattr(tool, '_run')):
            raise ValueError(f"Tool {tool.__class__.__name__} is missing the required '_run' method implementation.")

    # Create a new task with validated tools
        new_task = Task(
            agent=agent,
            description=description,
            expected_output=expected_output,
            output_file=output_file,
            tools=tools,
        )
        self.tasks.append(new_task)
        return new_task 

    def get_task_by_description(self, description):
        for task in self.tasks:
            if task.description == description:
                return task
        return None

    def JD_task(
        self,
        agent,
        Position,
        Number_of_Openings,
        Experience_Level,
        Branch,
        Location,
        Primary_Skills,
        Desired_Skills,
        Certifications,
        Job_Description,
    ):
        return Task(
            description=dedent(
                """
                 Create a brief job description for a specific role within the company. The job description should incorporate all relevant details, including the position title, number of openings, experience level, branch, location, primary and desired skills, certifications, and any other necessary information.
            """
            ),
            expected_output=dedent(
                f"""
               Give simple job description that includes:

                1. **Position**: {Position}.
                2. **Number of Openings**: {Number_of_Openings}.
                3. **Experience Level**:{Experience_Level}.
                4. **Branch**: {Branch}.
                5. **Location**: {Location}.
                6. **Primary Skills**: {Primary_Skills}.
                7. **Desired Skills**: {Desired_Skills}.
                8. **Certifications**: {Certifications}.
                9. **Job Description**: {Job_Description}.
                
            """
            ),
            verbose=True,
            output_file="job_description.md",
            agent=agent,
        )

    def converter_task(self, agent, input_file_name, output_file_name):
        return Task(
            description=f"Convert a Markdown file into PDF format using markdown_to_pdf converter tool. The Markdown file located at {input_file_name} should be processed and converted into a PDF file saved at {output_file_name}. Ensure that the PDF is properly formatted and reflects the content of the Markdown file accurately.",
            expected_output=f""" 1. Convert the Markdown file located at {input_file_name} into a PDF format using markdown_to_pdf converter tool.
            2. Save the converted PDF to the specified path: {output_file_name}.
            3. The final output should be a PDF file named {output_file_name}, which accurately represents the content of the Markdown file {input_file_name}.""",
            tools=[markdown_to_pdf],
            agent=agent,
            verbose=True,
        )

    def pdf_to_md_converter_task(self, agent, input_file):
        return Task(
            description=f"Convert a PDF file into Markdown format using the pdf_to_markdown converter tool. The PDF file located at {input_file} should be processed and converted into a Markdown file saved at output_file. Ensure that the Markdown file accurately represents the content of the PDF file.",
            expected_output=f"""1. Convert the PDF file located at {input_file} into Markdown format using the pdf_to_markdown converter tool.
            2. Save the converted Markdown to the specified path.
            3. The final output should be a Markdown file, which accurately represents the content of the PDF file {input_file}.""",
            tools=[pdf_to_markdown],
            input_file= "job_description.pdf",
            agent=agent,
            verbose=True,
        )

    def analysis_task(self, agent):
        return Task(
            description=(
                f"""
            Your task is to enhance a job description template to reflect current market trends and industry standards.

            **Steps to Follow:**
            1. **Retrieve the Template:** Use the {file_read_tool} to read and extract the content from the job description template located at the specified path.

            2. **Analyze Market Trends:** Utilize the {search_tool} to perform a web search and gather insights into the latest job market trends related to the position. Ensure that the search tool opens the required websites for scraping job data. Focus on:
            - Updated job titles, roles, and responsibilities.
            - In-demand skills and certifications.
            - Modern responsibilities and employer expectations.
            - Competitive company benefits and perks.

            3. **Ensure Web Scraping is Initiated:** Make sure that the Selenium Chromedriver opens the necessary websites for data scraping. Verify that the scraping process completes before proceeding with content enhancement.

            4. **Enhance the Content:** Refine the job description based on the collected data. Update the template to include:
            - **Position Details:** Modernized job titles, roles, and responsibilities.
            - **Required Skills:** Current high-demand skills.
            - **Certifications:** Relevant and up-to-date certifications.
            - **Responsibilities:** Responsibilities that align with contemporary job practices.
            - **Company Offerings:** Attractive benefits and perks for today’s job seekers.

            5. **Present the Output:** Deliver the updated job description in a well-structured format that includes:
            - The revised job description template.
            - A comparison showing how the updates align with market standards.
            - Recommendations for further enhancements if needed.

            Ensure that the final content is compelling and designed to attract top talent.
            """
            ),
            expected_output=(
                """
            1. **Updated Job Description Template:** A refined version of the original job description, incorporating modern market trends and industry standards. The updates should cover:
            - **Position Details:** Updated titles, roles, and responsibilities.
            - **Required Skills:** Relevant and high-demand skills.
            - **Certifications:** Current and applicable certifications.
            - **Responsibilities:** Aligned with contemporary job practices.
            - **Company Offerings:** Enhanced benefits and perks.
            """
            ),
        
           
            agent=agent,
            tools=[file_read_tool, search_tool],
            output_file="job_skills.md",
        )

    def linkedin_post_task(self, agent, email, password):
        return Task(
            description=(
                f"""
        Your task is to automate the process of posting content to LinkedIn using the provided custom tool.

        **Steps to Follow:**
        1. **Retrieve Content:** Use the provided Markdown file path to read the content to be posted.
        
        2. **Post Content to LinkedIn:** Utilize the `post_to_linkedin` tool to:
            - Log in to LinkedIn using the provided credentials.
            - Navigate to the LinkedIn post creation page.
            - Post the content from the Markdown file.
        
        3. **Verify Posting:** Ensure that the content is successfully posted to LinkedIn and that there are no errors during the process.
        
        **Inputs Required:**
        
        - `linkedin_email`: {email}The LinkedIn email address for logging in.
        - `linkedin_password`: {password }The LinkedIn password for logging in.

        **Expected Output:**
        - A success message confirming that the content has been posted to LinkedIn.
        - An error message if any issues occurred during the process.
        """
            ),
            expected_output=(
                """
        1. **Post Confirmation:** A message indicating successful posting to LinkedIn.
        
        2. **Error Handling:** If any errors occur, a detailed message describing the issue.
        
        Ensure that the posting process is completed successfully and that the content is visible on LinkedIn.
        """
            ),
            tools=[linkedin_post],
            agent=agent,
        )
    def seo_task(self, agent, topic):
        return Task(
            description=f'Develop core SEO strategy for a text-focused WordPress blog on {topic}',
            agent=agent,
            expected_output="""
                1. Primary keyword: [main keyword]
                2. Secondary keywords: [3-5 related keywords]
                3. Content structure:
                   - Main topic: [H1 equivalent]
                   - Subtopics: [3-5 H2 equivalents]
                4. Word count: [Recommended range for main content]
            """,
            tools=[search_tool],
        )

    def research_task(self, agent, topic, context):
        return Task(
            description=f'Gather essential information on {topic} for text-centric blog content',
            agent=agent,
            expected_output="""
                1. Key aspects: [5-7 main points]
                2. Current trends: [2-3 recent developments]
                3. Critical data: [3-5 relevant statistics or facts]
                4. Expert insights: [2-3 expert viewpoints, paraphrased]
                5. Unique angles: [1-2 fresh perspectives]
            """,
            tools=[search_tool],
            context=context,
        )

    def Company_Blog_Writer_Task(self, agent, topic, context):
        return Task(
            description=f"""Research and write engaging blog posts on {topic}, the content should reflect the company's expertise, address industry trends, and provide valuable insights to the target audience.""",
            agent=agent,
            expected_output="""
            Main topic: [Topic title]

                [Subtopic 1]
                [2-3 paragraphs of focused, informative and unique content]

                [Subtopic 2]
                [2-3 paragraphs of focused, informative and unique content]

                [Subtopic 3]
                [2-3 paragraphs of focused, informative and unique content]

                [Subtopic 4]
                [2-3 paragraphs of focused, informative and unique content]

                [Subtopic 5]
                [2-3 paragraphs of focused, informative and unique content]

                Note: Ensure each subtopic:
                - Integrates relevant keywords naturally
                - Includes at least one statistic or expert insight
                - Maintains coherent flow

                Don't Generate:
                - Introduction and Conclusion
                - Colon and Semincolon operation in the subtopic
                - Company name (eg. : IBM, Harvard Business, etc)
                - Don't write any company name in the result
                - Internal and External links
                - Reference sites
            """,
            context=context,
            output_file="outs/content.md",
        )
