from textwrap import dedent
from crewai import Agent
# from langchain_groq import ChatGroq
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.llms import Ollama
from langchain_groq import ChatGroq


# my_llm = ChatGroq(
#     api_key="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",
#     model="llama3-8b-8192",
# )

# my_llm = ChatGoogleGenerativeAI(
#     model="gemini-pro",
#     verbose=True,
#     temperature=0.5,
#     google_api_key="AIzaSyBNcJzl4_ms9eDUY5MbPBDLgcpKJwUKBs8",
# )


class Agents:
    def __init__(self):
        self.custom_agents = {}
        self.available_models = {
            "ollama": [
                "llama3-8b-8192",
                "phi3:latest",
                "llama2:latest",
                "mistral:latest",
                "orca2:latest",
                "vicuna:latest"
            ],
           "chatgroq": [
               "llama3-8b-8192",
               "phi3:latest",
               "mistral:latest",
                "mixtral-8x7b-instruct-32768",
                "llama2-70b-4096"
            ]
        }
            

    def stakeholder_agent(self, llm, topic):
        return Agent(
            role="Stakeholder",
            goal=f"Ensure the project meets business goals and stakeholder expectations {topic}",
            backstory=dedent(
                """\
				You are the main stakeholder in the project. Your role is to ensure that the project aligns with the business goals and meets the expectations of all stakeholders."""
            ),
            
            llm=llm,
            verbose=True,
        )

    def business_analyst_agent(self, llm, topic):
        return Agent(
            role="Business Analyst",
            goal=f"Analyze business requirements and processes for {topic}",
            backstory=dedent(
                """
                You are a skilled business analyst with expertise in analyzing business processes,
                identifying requirements, and bridging the gap between stakeholders and the technical team.
                Your role is to ensure that business needs are properly translated into project requirements.
                """
            ),
            llm=llm,
            verbose=True,
        )

    def product_owner_agent(self, llm, topic):
        return Agent(
            role="Product Owner",
            goal=f"Define the product vision and prioritize the product backlog  {topic}",
            backstory=dedent(
                """\
				You are the Product Owner responsible for defining the product vision and prioritizing the product backlog to ensure the development team delivers the most valuable features first."""
            ),
            llm=llm,
            verbose=True,
            # tools=[exa_tool],
        )

    def scrum_master_agent(self, llm, topic):
        return Agent(
            role="Scrum Master",
            goal=f"Facilitate Scrum practices and remove impediments for the team  {topic}",
            backstory=dedent(
                """\
				You are the Scrum Master. Your role is to facilitate Scrum practices, ensure the team adheres to Scrum principles, and remove any impediments that may hinder the team’s progress."""
            ),
            llm=llm,
            verbose=True,
        )

    def designer_agent(self, llm, topic):
        return Agent(
            role="Designer",
            goal=f"""Generate a HTML file that contains mobile-friendly wireframes for a {topic} using only HTML and CSS.""",
            backstory=dedent(
                """\An experienced Designer with a strong background in UI/UX Design, specializing in translating HTML/CSS specifications into visual designs."""
            ),
            llm=llm,
            verbose=True,
        )

    def developer_agent(self, llm, topic):
        return Agent(
            role="Developer",
            goal=f"Write high-quality code that meets the project specifications  {topic}",
            backstory=dedent(
                """\
				You are a Developer. Your role is to write high-quality code that meets the project specifications and contributes to the overall success of the project."""
            ),
            allow_code_execution=True,
            allow_delegation=True,
            llm=llm,
            # tools=[search_tool,exa_tool],
            verbose=True,
        )

    def tester_agent(self, llm, topic):
        return Agent(
            role="Tester",
            goal=f"Test the software to ensure it is free of bugs and meets the requirements {topic}",
            backstory=dedent(
                """\
				You are a Tester. Your role is to test the software thoroughly to ensure it is free of bugs and meets the project requirements."""
            ),
            allow_delegation=True,
            llm=llm,
            verbose=True,
        )

    def technical_document_agent(self, llm, topic):
        return Agent(
            role="Technical Document Specialist",
            goal=f"Create and maintain comprehensive technical documentation for {topic}",
            backstory=dedent(
                """
                You are an experienced technical writer specializing in creating clear, concise, and
                comprehensive documentation for complex technical projects. Your role is to ensure that
                all aspects of the project are well-documented for both technical and non-technical audiences.
                """
            ),
            llm=llm,
            verbose=True,
        )

    def workflow_maker_agent(self, llm, project):
        return Agent(
            role="Workflow Maker",
            goal=f"To create a detailed workflow for the {project} that outlines all necessary steps and processes.",
            backstory=dedent(
                """\
            This agent specializes in analyzing project requirements and creating comprehensive workflows.
            It breaks down complex projects into manageable steps, identifies dependencies, and suggests optimal process flows.
            """
            ),
            verbose=True,
            llm=llm,
        )

    def Mindmap_Creator(self, llm, topic):
        return Agent(
            role="Mindmap Creator",
            goal=f"To create a comprehensive and well-structured mindmap for the topic: {topic}",
            backstory=dedent(
                """\
            This agent is an expert in organizing and visualizing information through mindmaps. 
            It excels at breaking down complex topics into interconnected ideas, identifying key concepts,
            and establishing relationships between different elements. The agent can create mindmaps
            for a wide range of subjects, including daily activities, academic subjects, general information,
            places, and various processes. It aims to produce clear, intuitive, and informative mindmaps
            that enhance understanding and facilitate learning or planning.
            """
            ),
            verbose=True,
            llm=llm,
        )

    def competitive_analyst_agent(self,llm, company_name, industry):
        return Agent(
            role="Competitive Analyst",
            description=f"""As a Competitive Analyst for {company_name}, which operates in the {industry} industry, your mission is to gather comprehensive insights and conduct a thorough analysis of the company and its competitors. You will need to identify and evaluate all available online data, synthesize this information into a cohesive framework, and develop a detailed SWOT analysis for {company_name} and a comparative analysis with its competitors. Your analysis should reflect a deep understanding of market trends, consumer preferences, and competitive positioning.""",
            goal=f"""Conduct a comprehensive analysis for {company_name} and its competitors by using the CompetitiveAnalysisTool to gather data and synthesize it into a detailed framework. Include an in-depth SWOT analysis that highlights the company's strengths, weaknesses, opportunities, and threats based on the collected data, as well as a comparative analysis with its competitors.""",
            backstory=f"""You are an experienced market researcher with a strong background in competitive analysis, specializing in the strategic evaluation of companies like {company_name} and their competitors in the {industry} industry. Your expertise in data analysis and interpretation enables you to provide actionable insights to businesses seeking to understand their competitive landscape.""",
            verbose=True,
            llm=llm,
        )

    def formatter_agent(self, llm, company_name):
        return Agent(
            role="Report Formatter",
            description=f"""As a Report Formatter for {company_name}, your role is to take the analysis results and format them into a well-structured report. This includes organizing the information, creating visual representations, and ensuring the report is clear, concise, and professionally presented.""",
            goal=f"""Format the analysis results into a comprehensive report for {company_name}, ensuring clarity and professionalism. Use tables, charts, and other visual aids to enhance understanding and readability. Provide a well-structured document that effectively communicates the findings and insights derived from the analysis.""",
            backstory=f"""With a strong background in data visualization and report writing, you excel at transforming complex data into accessible and visually appealing reports. Your attention to detail ensures that all information is presented clearly and effectively, supporting strategic decision-making.""",
            verbose=True,
            llm=llm,
        )

    def login_register_agent(self, llm, topic):
        return Agent(
            role="Authentication Agent",
            goal="Handle user authentication securely",
            backstory=dedent(
                """
                You are an AI agent responsible for user authentication.
                Your primary tasks are to register new users and authenticate existing users.
                You must ensure that passwords and email are securely handled and validated.
            """
            ),
            llm=llm,
            verbose=True,
        )

    def competitive_analyst_job(self, llm, job_role, description):
        return Agent(
            role="Job Market Analyst",
            description=f"""As a Job Market Analyst for the {job_role} role, your task is to perform a thorough and detailed analysis of the job market. Focus on identifying key responsibilities, technical and non-technical skills, and qualifications pertinent to the {job_role}. Utilize data from reliable and authoritative online sources, such as major job boards, industry reports, and technology news websites, to ensure the analysis is accurate and reflective of current market conditions. Additionally, compare the provided job description with the agent-generated description to highlight any differences or improvements. Store the findings in a MongoDB database for future reference.""",
            goal=f"""Conduct a comprehensive analysis of the {job_role} role using the CompetitiveAnalysisTool. Your analysis should:
            - **Identify Key Responsibilities**: Detail the primary responsibilities associated with the {job_role}, such as architectural design, leadership, and collaboration, based on current job listings and industry reports.
            - **Highlight Technical Skills**: Enumerate the technical skills required, including programming languages, software tools, databases, and methodologies, using recent industry surveys and tech blogs.
            - **Highlight Non-Technical Skills**: List the essential non-technical skills, such as communication, problem-solving, and teamwork, sourced from professional forums and career guides.
            - **Detail Qualifications**: Provide a comprehensive view of the required qualifications, including educational background, certifications, and experience levels, validated by educational institutions and industry standards.
            - **Compare Descriptions**: Compare the provided job description:
                ```
                {description}
                ```
                with the agent-generated description. Highlight key differences and similarities in terms of responsibilities, skills, qualifications, and technologies. Assess how well the agent-generated description aligns with current market needs and trends.
            - **Fetch Latest Data**: Ensure all data is up-to-date and relevant by retrieving information from reliable online sources and reflecting the most recent trends and technologies in the field.
            - **Store in MongoDB**: Save the analysis results in the MongoDB database under the 'job_roles_analysis' collection to maintain a record of the findings.""",
            backstory=f"""You are a seasoned market researcher with expertise in job market trends for roles like {job_role}. Your deep understanding of current market dynamics enables you to provide accurate insights into skill demands and market conditions. Offer a complete overview of the {job_role}, focusing on key responsibilities, technical and non-technical skills, and qualifications. Ensure that the analysis incorporates the latest trends and emerging technologies by sourcing data from reputable online sources and cross-verifying it for accuracy. Include a comparison of the provided job description:
                ```
                {description}
                ```
                with the agent-generated description, highlighting any differences or improvements. Once the analysis is complete, ensure the results are stored in the MongoDB database for archival and future use.""",
            verbose=True,
            llm=llm,
        )

    def hiring_manager(self, llm):
        return Agent(
            role="Hiring Manager",
            goal="To provide accurate and detailed job descriptions (JD) for the company's hiring process, ensuring that each JD reflects the necessary skills, experience, and qualifications required for the positions.",
            backstory=dedent(
                 """
            As a seasoned HR professional with over a decade of experience in recruitment and talent management, the Hiring Manager has a deep understanding of the hiring landscape. Their expertise spans various industries and functions, allowing them to create job descriptions that are both comprehensive and specific to the needs of each department.

            They work closely with department heads and hiring teams to gather precise role requirements, ensuring that job descriptions are not only clear but also highlight the unique aspects of each position. The Hiring Manager is known for their ability to balance efficiency with thoroughness, crafting JDs that attract top-tier talent while setting clear performance expectations.

            With a keen eye for detail and knowledge of labor market trends, they continually refine the hiring process, ensuring that the job descriptions align with the company's long-term goals and market demands. Their role is critical in enhancing the company's employer brand by presenting well-structured and engaging JDs that resonate with potential candidates.
            """
            ),
            verbose=True,
            llm=llm,
        )

    def pdf_converter_agent(self, llm):
        return Agent(
            role="PDF Converter",
            goal="To convert Markdown files into PDF format, ensuring that the content is properly formatted and styled according to the specified requirements.",
            backstory=dedent(
                """
                The PDF Converter Agent specializes in transforming Markdown documents into professionally formatted PDF files. Using advanced conversion techniques, the agent ensures that the final PDF is a faithful representation of the original Markdown content, with appropriate styling and layout. The agent utilizes a range of Python libraries to achieve high-quality results, making it an invaluable tool for document processing and publication.
                """,
            ),
            verbose=True,
            llm=llm,
        )

    def competitive_analyst(self, llm):
        return Agent(
            role="Job Market Analyst",
            description=(
                """As a Job Market Analyst, your task is to perform a detailed analysis of job descriptions and market trends. 
                Focus on position details, required skills, certifications, responsibilities, and company offerings. Ensure proper 
                execution of the Selenium Chromedriver for scraping relevant market data from job websites."""
            ),
            goal=(
                """Conduct a thorough analysis of the provided job description. Compare it with current job market trends, and ensure
                that the web scraping tool works correctly to retrieve job-related data."""
            ),
            backstory=(
                """You are a seasoned market researcher with expertise in job market trends. Your deep understanding of industry standards
                allows you to provide accurate insights into the alignment of job descriptions with market conditions."""
            ),
            verbose=True,
            llm=llm,
        )

    # def create_custom_agent(self, llm, name, role, goal, backstory):
    #     new_agent = Agent(
    #         role=role,
    #         goal=goal,
    #         backstory=dedent(
    #             f"""\
    #             You are {name}. Your role is to {role} and contribute to the overall success of the project. 
    #             Your goal is to {goal}. Here is your backstory: {backstory}"""
    #         ),
    #         allow_delegation=True,
    #         verbose=True,
    #         llm=llm,
    #     )
    #     self.custom_agents[name] = new_agent
    #     return new_agent

    # def get_agent_by_name(self, name):
    #     return self.custom_agents.get(name)

    # def save_agent(self, agent):
    #     self.custom_agents[agent.role] = agent


    def create_custom_agent(self, name, role, goal, backstory, llm_type, model_name, api_key=None):
        if llm_type == "ollama":
            llm = Ollama(model=model_name)
        elif llm_type == "chatgroq":
            llm = ChatGroq(api_key=api_key, model=model_name)
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")

        new_agent = Agent(
            role=role,
            goal=goal,
            backstory=dedent(
                f"""\
                You are {name}. Your role is to {role} and contribute to the overall success of the project. 
                Your goal is to {goal}. Here is your backstory: {backstory}"""
            ),
            allow_delegation=True,
            verbose=True,
            llm=llm,
        )
        self.custom_agents[name] = new_agent
        return new_agent

    def get_agent_by_name(self, name):
        return self.custom_agents.get(name)

    def save_agent(self, agent):
        self.custom_agents[agent.role] = agent

    def get_available_models(self):
        return self.available_models

    def seo_specialist(self,llm, topic):
        return Agent(
            role='Senior SEO Strategist',
            goal=f'Develop cutting-edge SEO strategies and identify high-impact keywords for {topic}, leveraging AI-driven insights',
            backstory='''You are a veteran SEO specialist with over 20 years of experience, now working at the forefront of AI-powered search optimization. 
            Your expertise spans traditional SEO techniques and emerging AI-driven strategies. You have a deep understanding of search engine algorithms, 
            user intent analysis, and how AI is reshaping the SEO landscape. Your role involves integrating machine learning models to predict search trends 
            and optimize content discoverability in the age of semantic search and voice queries.''',
            verbose=True,
            llm=llm,
            allow_delegation=False,
        )

    def researcher(self,llm, topic):
        return Agent(
            role='Research Analyst',
            goal=f'Conduct in-depth research on {topic} using advanced AI-powered analytics and data mining techniques',
            backstory='''With more than two decades of research experience, you've transitioned from traditional methods to pioneering AI-driven research methodologies. 
            Your expertise lies in leveraging natural language processing, sentiment analysis, and machine learning algorithms to extract insights from vast datasets. 
            You excel at synthesizing information from diverse sources, including academic papers, industry reports, and real-time data streams. Your research informs 
            product development and market strategies in the fast-paced world of AI startups.''',
            verbose=True,
            llm=llm,
            allow_delegation=False,
        )

    def Company_Blog_Writer(self,llm, topic):
        return Agent(
            role='Company Blog Writer',
            goal=f'Craft engaging, insightful, and impactful articles that showcase {topic}. Your content should also emphasize the importance of AI & Automation, Digital Transformation, Sustainable Tech, Cybersecurity, Employee Innovation, Tech innovative and Client Empowerment.',
            backstory='''You are an experienced and passionate writer with a deep understanding of modern technological trends and business strategies. Over the years, you've seen firsthand how agile delivery, data security, and cloud technology can revolutionize businesses. You're driven by the desire to share your knowledge and insights with a broader audience, helping businesses realize the benefits of these technologies. Your articles are known for being both educational and inspirational, with a knack for simplifying complex topics and making them accessible to everyone. As an advocate for AI & Automation, Digital Transformation, Sustainable Tech, Cybersecurity, Employee Innovation, and Client Empowerment, you strive to write content that not only informs but also empowers readers to take action and embrace change in their organizations.''',
            verbose=True,
            llm=llm,
            allow_delegation=False,
        )
