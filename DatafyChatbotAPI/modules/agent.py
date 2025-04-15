# agent.py
import os
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.schema import Document, HumanMessage, SystemMessage, AIMessage
from langchain.chains import LLMChain
from modules.retrievers import GuidanceRetriever, RecommendationRetriever, MotivationRetriever, CoachRetriever

class DeciderAgent:
    """
    Kullanıcı sorgusuna göre hangi ajanın kullanılacağına karar veren sınıf
    """
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        # Decider için LLM modeli
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini", 
            openai_api_key=openai_api_key,
            temperature=0.0  # Tutarlı kararlar için temperature düşük
        )
        
        # Decider prompt'u
        self.system_prompt = """
        Act like an intelligent query classification system for an educational assistant platform.
        You are responsible for routing user queries to the most suitable expert agent based on the intent and content of each query. 
        This routing system is designed to ensure users receive the most relevant and helpful support depending on whether they need guidance, recommendations, or motivation.
        Your job is to classify each user query into one of the three following agent categories, based strictly on the query's objective:

        1.Guidance (Agent: "rehberlik")
        
        Use this category when the user is asking about:
        -Career advice
        -Education planning
        -University/department/school selection
        -Strategies for exam preparation
        -General educational direction or academic decision-making

        2.Recommendation (Agent: "öneri")
        
        Use this category when the user is looking for:
        -Study materials or tools
        -Learning techniques or hacks
        -Subject-specific resources
        -Learning platforms, books, or apps
        -Suggestions to improve their learning process

        3.Motivation (Agent: "motivasyon")

        Use this category when the user seems to be:
        -Lacking motivation to study
        -Feeling stressed, overwhelmed, or anxious
        -Looking for encouragement or inspiration
        -Needing emotional or mental support for academic performance

        4.Coach Matching (Agent: "koç")

        Use this category when the user is seeking:
        -Personalized coaching recommendations
        -Help finding a tutor or mentor

        Final Instructions:

        -You MUST return only one of the following words as your answer: "rehberlik", "öneri", "koç" or "motivasyon" — no other text, punctuation, or explanation.
        -Your decision MUST be based solely on the user’s intent, even if the query is vague or ambiguous.
        -If the query contains elements of multiple categories, choose the primary intent.
        -DO NOT ask clarifying questions — make your best decision based on the information provided.
        -Be extremely strict with categorization logic. NEVER guess randomly.

        Take a deep breath and work on this problem step-by-step.
        """
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_prompt),
            HumanMessagePromptTemplate.from_template("{query}")
        ])
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    async def decide_agent(self, query: str) -> str:
        """
        Kullanıcı sorgusuna göre hangi ajanın kullanılacağına karar verir
        
        Args:
            query: Kullanıcı sorusu
            
        Returns:
            str: Seçilen ajan adı ("rehberlik", "öneri", "motivasyon" veya "koç")
        """
        try:
            # LLM'den ajana karar vermesini iste
            response = await self.chain.arun(query=query)
            
            # Cevabı temizle
            agent_type = response.strip().lower()
            
            # Geçerli bir ajan mı kontrol et
            if agent_type in ["rehberlik", "öneri", "motivasyon", "koç"]:
                return agent_type
            else:
                print(f"Geçersiz ajan tipi: {agent_type}, varsayılan olarak 'rehberlik' kullanılıyor")
                return "rehberlik"  # Varsayılan olarak rehberlik ajanı kullan
        
        except Exception as e:
            print(f"Ajan seçme hatası: {str(e)}")
            return "rehberlik"  # Hata durumunda varsayılan olarak rehberlik ajanı kullan


class BaseAgent:
    """
    Tüm agentlar için temel sınıf
    """
    def __init__(self, 
                 openai_api_key: str, 
                 agent_name: str,
                 system_prompt: str,
                 milvus_host: str = "localhost", 
                 milvus_port: str = "19530"):
        self.openai_api_key = openai_api_key
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.milvus_host = milvus_host
        self.milvus_port = milvus_port
        
        # LLM modeli
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini", 
            openai_api_key=openai_api_key,
            temperature=0.05  
        )
        
        # Prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("Kullanıcı Sorusu: {query}\n\nİlgili Bilgiler: {context}")
        ])
        
        # Chain oluştur
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        
        # Retriever
        self.retriever = None  
    
    async def get_response(self, query: str) -> Dict[str, str]:
        """
        Kullanıcı sorgusuna yanıt üretir
        
        Args:
            query: Kullanıcı sorusu
            
        Returns:
            Dict: Agent adı ve yanıt içeren sözlük
        """
        if not self.retriever:
            raise ValueError(f"{self.agent_name} ajanının retriever'ı yapılandırılmamış")
            
        # İlgili belgeleri getir
        try:
            docs = await self.retriever.get_relevant_documents(query)
            # Belgelerin içeriğini birleştir
            context = "\n\n".join([doc.page_content for doc in docs]) if docs else "İlgili bilgi bulunamadı."
            
            # Çalışıp çalışmadığının kontrolü
            # TAM PROMPTU EKRANA BASTIR
            """print("\n" + "="*50)
            print(f"AJAN: {self.agent_name}")
            print("="*50)
            print("SYSTEM PROMPT:")
            print(self.system_prompt)
            print("\nUSER PROMPT:")
            print(f"Kullanıcı Sorusu: {query}\n\nİlgili Bilgiler: {context}")
            print("="*50 + "\n")
            # Yanıt üret"""
            response = await self.chain.arun(query=query, context=context)
            
            return {
                "agent": self.agent_name,
                "response": response
            }
        except Exception as e:
            print(f"{self.agent_name} ajanı yanıt üretme hatası: {str(e)}")
            return {
                "agent": self.agent_name,
                "response": f"Üzgünüm, yanıt üretirken bir hata oluştu: {str(e)}"
            }


class GuidanceAgent(BaseAgent):
    """
    Rehberlik konusunda özelleşmiş agent
    """
    def __init__(self, openai_api_key: str, milvus_host: str = "localhost", milvus_port: str = "19530"):
        # Bu promptun da değişmesi lazım daha iyi bir şey bulunabilir
        system_prompt = """
        Act like an expert in educational and career guidance.
        You have been supporting students across all levels of education for over 20 years.
        Your expertise lies in helping them navigate critical decisions in their academic journey and career development.
        You are empathetic, informed, and capable of adapting your advice based on the student's age, education level, and personal needs.
        
        Your primary goal is to provide personalized, accurate, and actionable guidance to students. You specialize in the following areas:
        
        -Exam strategies and effective study planning
        -Choosing the right school, academic department, or university
        -Career path exploration and professional direction
        -Understanding different education systems and transitions
        -Learning techniques, productivity tools, and time management
        
        Your response must always meet these 5 criteria:
        
        1.Use clear, concise, and age-appropriate language that students can easily understand.
        2.Tailor your answer to the student's level (e.g., middle school, high school, university).
        3.Use only the provided or referenced information — NEVER make assumptions or fabricate content.
        4.Maintain a supportive, mentoring, and encouraging tone.
        5.Whenever possible, include relevant, up-to-date sources or resources (websites, tools, links) that the student can consult for further support.

        Final Instructions:

        -You MUST respond in Turkish language.
        -Only provide guidance based on the input given to you. Do not introduce new ideas or make up information.
        -If you receive a question that is beyond your knowledge or not covered in the provided data, admit it honestly.
        -In such cases, suggest credible institutions, professionals, or websites where the student can get accurate answers.
        
        Take a deep breath and work on this problem step-by-step.
        """
        
        super().__init__(
            openai_api_key=openai_api_key,
            agent_name="rehberlik",
            system_prompt=system_prompt,
            milvus_host=milvus_host,
            milvus_port=milvus_port
        )
        
        # GuidanceRetriever'ı oluştur
        self.retriever = GuidanceRetriever(
            openai_api_key=openai_api_key,
            milvus_host=milvus_host,
            milvus_port=milvus_port
        )


class RecommendationAgent(BaseAgent):
    """
    Öneriler konusunda özelleşmiş agent
    """
    def __init__(self, openai_api_key: str, postgre_url: str = "postgresql://postgres:1234@localhost:5432/postgres"):
        system_prompt = """
        Act like an expert in educational resources and study strategies.
        You have been helping students of all ages discover the most effective learning materials and study techniques for over 20 years.
        Your job is to recommend customized, practical, and up-to-date resources that match the student's specific needs, academic level, and learning preferences.
        
        You specialize in the following areas:

        -Recommending books, online courses, video lessons, podcasts, apps, and other educational materials
        -Teaching efficient study methods and productivity strategies
        -Suggesting subject-specific learning approaches (e.g., for math, language, science)
        -Providing self-assessment and practice tools for reinforcing knowledge
        -Introducing technology-assisted learning tools (e.g., flashcard apps, AI tutors, gamified platforms)
        
        Your recommendations must always follow these 5 guidelines:
        
        1.Tailor suggestions to the student’s academic level and specific learning goals (e.g., high school student preparing for math exams, university student struggling with focus).
        2.Offer diverse and alternative resources (e.g., visual, auditory, interactive), so students can choose what works best for them.
        3.Explain the strengths of each resource or technique — what makes it effective, who it’s best for, and how to use it.
        4.Include concrete, actionable, and easy-to-apply advice — avoid vague or generic suggestions.
        5.Prioritize current, accessible, and ideally free or low-cost resources — clearly state availability and access options.

        Final Instructions:

        -You MUST respond in Turkish language.
        -Respond only with the information provided to you. Do not invent or assume anything.
        -Avoid overly technical or academic language — keep it simple, student-friendly, and encouraging.
        -If a question is outside your knowledge or beyond the given data, admit it clearly and suggest where the student can find accurate information (e.g., trusted websites or educators).
        -Take a deep breath and work on this problem step-by-step.
        """
        
        super().__init__(
            openai_api_key=openai_api_key,
            agent_name="öneri",
            system_prompt=system_prompt,
        )
        
        # RecommendationRetriever'ı oluştur
        self.retriever = RecommendationRetriever(
            postgre_url=postgre_url,
        )
        
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=openai_api_key,
            temperature=0.05  
        )
        
        # Chain'i güncelle
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    async def extract_topic_and_kind(self, query: str) -> tuple[str, str]:
            """
            LLM kullanarak kullanıcı sorgusundan topic ve kind değerlerini çıkarır.
            """
            # Create a chat-style prompt
            prompt = ChatPromptTemplate.from_messages([
                HumanMessagePromptTemplate.from_template("""
                Act like an expert text classification model specialized in educational content.
                You have been trained to categorize Turkish student queries into specific exam subjects and difficulty levels for study resource recommendations.
                Your task is to analyze a given user query in natural Turkish and determine:
                    
                    1.The subject area ("topic") the query refers to.
                    2.The difficulty level or resource type ("kind") requested.

                Follow these steps to perform the classification:

                Step 1 — Understand Subject ("topic"):

                Check if the query refers to a specific subject or course. Match the query to one of the following valid values:

                Matematik (Math):
                -tyt_matematik
                -ayt_matematik

                Geometri (Geometry):
                -geometri

                Fen Bilimleri (Science):
                -tyt_fizik
                -ayt_fizik, 
                -tyt_kimya, 
                -ayt_kimya,
                -tyt_biyoloji,
                -ayt_biyoloji

                Sosyal Bilimler ve Dil (Social Studies & Language):

                -dilbilgisi
                -edebiyat
                -tarih
                -coğrafya

                Choose only one most relevant topic. If the subject is ambiguous or unclear, choose the most likely one.

                Step 2 — Determine Difficulty Level ("kind"):

                Identify the difficulty level or intent behind the user's request. Match it to one of the following values:

                -kolay_kaynak: Request for easy-level materials
                -orta_kaynak: Request for medium/intermediate-level materials
                -zor_kaynak: Request for difficult/advanced-level materials
                -link: Asking for a direct link or resource

                Choose the most appropriate label based on intent and language cues (e.g. “kolay soru”, “zor kaynak”, “link atabilir misin?”).

                Step 3 — Output Format:

                Return only the result in the following format:
                
                topic: <topic_value>
                kind: <kind_value>
                
                Replace <topic_value> and <kind_value> with the detected values. Do not include anything else in the output.

                Example Input:

                Karmaşık sayılarla ilgili zor seviye AYT matematik kaynaklarına ihtiyacım var.
                
                Example Output:

                topic: ayt_matematik
                kind: zor_kaynak
                                                         
                User Query: {query}
                                                         
                Take a deep breath and work on this problem step-by-step.
        """)
            ])

            extractor_chain = LLMChain(llm=self.llm, prompt=prompt)

            try:
                result = await extractor_chain.arun(query=query)
                topic = "unknown"
                kind = "link"

                lines = result.strip().splitlines()
                for line in lines:
                    if line.lower().startswith("topic:"):
                        topic = line.split(":", 1)[1].strip().lower()
                    elif line.lower().startswith("kind:"):
                        kind = line.split(":", 1)[1].strip().lower()

                return topic, kind

            except Exception as e:
                print(f"[extract_topic_and_kind ERROR]: {e}")
                return "unknown", "link"

    async def get_response(self, query: str) -> Dict[str, str]:
        if not self.retriever:
            raise ValueError(f"{self.agent_name} ajanının retriever'ı yapılandırılmamış")

        try:
            topic, kind = await self.extract_topic_and_kind(query)

            docs = await self.retriever.get_relevant_documents(topic=topic, kind=kind)
            context = "\n\n".join([doc.page_content for doc in docs]) if docs else "İlgili bilgi bulunamadı."

            response = await self.chain.arun(query=query, context=context)

            return {
                "agent": self.agent_name,
                "response": response
            }

        except Exception as e:
            print(f"{self.agent_name} ajanı hata verdi: {e}")
            return {
                "agent": self.agent_name,
                "response": f"Üzgünüm, bir hata oluştu: {e}"
            }

class MotivationAgent(BaseAgent):
    """
    Motivasyon konusunda özelleşmiş ajan
    """
    def __init__(self, openai_api_key: str, milvus_host: str = "localhost", milvus_port: str = "19530"):
        system_prompt = """
        Act like a certified motivation and inspiration coach who specializes in academic support.
        You have helped thousands of students overcome anxiety, procrastination, self-doubt, and burnout across all levels of education for over 15 years.
        You are deeply empathetic, emotionally intelligent, and use evidence-based motivational psychology to inspire change.
        
        Your mission is to help students:

        -Regain or maintain study motivation
        -Cope with stress, anxiety, and mental fatigue
        -Develop self-discipline and achieve goals
        -Overcome fear of failure and procrastination
        -Cultivate positive thinking and mental resilience

        When crafting your response:

        1.Always show empathy and understanding — acknowledge the student’s feelings and make them feel seen and heard.
        2.Use an inspiring and empowering tone — your words should energize, uplift, and encourage students to keep going.
        3.Offer realistic and actionable strategies — no generic “just try harder” tips; focus on what actually works.
        4.Take a warm and personalized approach — adapt your message to the user’s emotional state, age, and context.
        5.Rely on science-backed techniques — such as cognitive-behavioral tools, goal-setting frameworks, stress regulation methods, and growth mindset principles.

        Final Instructions:

        -You MUST respond in Turkish language.
        -Base your response only on the user’s input and the context provided. DO NOT fabricate or add unsupported claims.
        -If the query exceeds your scope or you’re unsure, be honest. In that case, you MUST gently direct the student to reliable mental health or academic counseling services.
        -NEVER use harsh, judgmental, or dismissive language. Always be supportive, hopeful, and constructive.

        Take a deep breath and work on this problem step-by-step.
        """
        
        super().__init__(
            openai_api_key=openai_api_key,
            agent_name="motivasyon",
            system_prompt=system_prompt,
            milvus_host=milvus_host,
            milvus_port=milvus_port
        )
        
        # MotivationRetriever'ı oluştur
        self.retriever = MotivationRetriever(
            openai_api_key=openai_api_key,
            milvus_host=milvus_host,
            milvus_port=milvus_port
        )
        
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=openai_api_key,
            temperature=0.05  
        )
        
        # Chain'i güncelle
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

class CoachAgent(BaseAgent):
    """
    Koç önerileri için özelleşmiş ajan
    """
    def __init__(self, openai_api_key: str, milvus_host: str = "localhost", milvus_port: str = "19530"):
        system_prompt = """
    Act like a professional education coach-matching expert.
    You have helped thousands of students find the right coach to boost their academic performance and exam success.
    You deeply understand different student types, coaching styles, and exam preparation dynamics in Turkey.
    Your task is to recommend the most suitable education coaches for students based on their needs, goals, and preferences.

    Use the following criteria to guide your recommendations:

    -Coach’s exam background and experience (e.g., TYT, AYT, university entrance exams)
    -Whether the coach is a repeat student or not.
    -Strong sides of the coach and exam experience (e.g., the topics coach is good at)
    -Coaching style and whether it matches the student's personality and study habits
    -Fee and budget compatibilty with the student.

    Follow these steps:

    1.Depending on the needs of the student recommend 2-3 coaches.
    2.For each coach provide the a motivative information which consists of 3-4 sentences according to the following template: 
    -Why this is a compatible match? (Which sides of the coach are compatible for the student and makes him/her a better overall pick?)
    -Coach's background and experience: How does the coach's background and experience contribute to the student?
    -How will the coach benefit the student according to his/her background?
    
    Final Instructions:
    
    -You MUST use a motivative and sincere language.
    -The sentences MUST be short but easy to understand.
    -You MUST provide the information in Turkish language.
    -You MUST provide the information based on the student's needs and the context provided.

    Take a deep breath and work on this problem step-by-step.
        """
        
        super().__init__(
            openai_api_key=openai_api_key,
            agent_name="koç",
            system_prompt=system_prompt,
            milvus_host=milvus_host,
            milvus_port=milvus_port
        )
        
        # CoachRetriever'ı import ve initialize et
        self.retriever = CoachRetriever(
            openai_api_key=openai_api_key,
            milvus_host=milvus_host,
            milvus_port=milvus_port
        )
        
        # LLM'i özelleştir
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=openai_api_key,
            temperature=0.05  
        )
        
        # Coach agent için prompt template'i güncelle
        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("Öğrenci Mesajı: {query}\n\nÖnerilen Koçlar: {coaches}")
        ])
        
        # Chain'i güncelle
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    async def get_response(self, query: str) -> Dict[str, str]:
        """
        Öğrenci sorgusuna göre koç önerileri verir
        
        Args:
            query: Öğrenci sorusu
            
        Returns:
            Dict: Agent adı ve yanıt içeren sözlük
        """
        try:
            # Öğrenci ihtiyaçlarını analiz et
            filters = await self.retriever.analyze_student_needs(query)
            
            # Uygun koçları bul
            coach_results = await self.retriever.search_coaches(query, filters, top_k=3)
            
            if not coach_results or len(coach_results[0]) == 0:
                return {
                    "agent": self.agent_name,
                    "response": "Üzgünüm, kriterlerinize uygun koç bulamadım. Lütfen farklı kriterlerle tekrar deneyin veya kriterlerinizi biraz genişletin."
                }
            
            # Koç bilgilerini formatla
            coaches_info = ""
            for i, hit in enumerate(coach_results[0]):
                coach = hit.entity
                coaches_info += f"Koç {i+1}: {coach.get('isim_soyisim')}\n"
                coaches_info += f"Okul/Bölüm: {coach.get('okul')} - {coach.get('bolum')}\n"
                coaches_info += f"Biyografi: {coach.get('biyografi')}\n"
                coaches_info += f"Koçluk Ücreti: {coach.get('kocluk_ucreti')} TL\n"
                coaches_info += f"Tecrübe: {coach.get('tecrube_sene')} yıl\n"
                coaches_info += f"Mezuna Kaldı: {'Evet' if coach.get('mezuna_kaldi') else 'Hayır'}\n"
                coaches_info += f"Koçluk Alanı: {coach.get('kocluk_alani')}\n"
                coaches_info += f"Güçlü Alanlar: {coach.get('guclu_alanlar')}\n"
                coaches_info += f"Son TYT Derecesi: {coach.get('tyt_derece_son')}\n"
                coaches_info += f"Son Sayısal Derecesi: {coach.get('sayisal_derece_son')}\n"
                coaches_info += f"Son Sözel Derecesi: {coach.get('sozel_derece_son')}\n"
                coaches_info += f"Son EA Derecesi: {coach.get('ea_derece_son')}\n"
                coaches_info += f"Benzerlik Skoru: {hit.score:.4f}\n\n"
            
            # Öneriler ve açıklamalar oluştur
            response = await self.chain.arun(query=query, coaches=coaches_info)
            
            return {
                "agent": self.agent_name,
                "response": response
            }
        except Exception as e:
            print(f"Koç önerileri oluşturma hatası: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {
                "agent": self.agent_name,
                "response": f"Üzgünüm, koç önerileri oluşturulurken bir hata oluştu: {str(e)}"
            }


class EducationAgentSystem:
    """
    Eğitim ajan sistemini yöneten ana sınıf
    """
    def __init__(self, openai_api_key: str, milvus_host: str = "localhost", milvus_port: str = "19530", postgre_url: str = "postgresql://postgres:1234@localhost:5432/postgres"):
        self.openai_api_key = openai_api_key
        self.milvus_host = milvus_host
        self.milvus_port = milvus_port
        
        # Decider ajanını oluştur
        self.decider = DeciderAgent(openai_api_key)
        
        # Ajanları oluştur
        self.agents = {
            "rehberlik": GuidanceAgent(openai_api_key, milvus_host, milvus_port),
            "öneri": RecommendationAgent(openai_api_key, postgre_url),
            "motivasyon": MotivationAgent(openai_api_key, milvus_host, milvus_port),
            "koç": CoachAgent(openai_api_key, milvus_host, milvus_port)
        }
    
    async def process_query(self, query: str) -> Dict[str, str]:
        """
        Kullanıcı sorgusunu işler ve uygun ajandan yanıt alır
        
        Args:
            query: Kullanıcı sorusu
            
        Returns:
            Dict: Agent adı ve yanıt içeren sözlük
        """
        try:
            # Hangi ajanın kullanılacağına karar ver
            agent_type = await self.decider.decide_agent(query)
            print(f"Seçilen ajan: {agent_type}")
            
            # Uygun ajanı seç
            if agent_type in self.agents:
                agent = self.agents[agent_type]
            else:
                print(f"Bilinmeyen ajan tipi: {agent_type}, varsayılan olarak rehberlik kullanılıyor")
                agent = self.agents["rehberlik"]
            
            # Seçilen ajandan yanıt al
            return await agent.get_response(query)
            
        except Exception as e:
            print(f"Sorgu işleme hatası: {str(e)}")
            return {
                "agent": "sistem",
                "response": f"Sorgunuz işlenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin."
            }
