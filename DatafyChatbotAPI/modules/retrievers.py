import os
import uuid
import psycopg2
from typing import List, Dict, Any, Optional
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Milvus
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, PyPDFLoader, CSVLoader
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.chat_models import ChatOpenAI
from pymilvus import connections, utility, Collection


class BaseRetriever:
    def __init__(self, openai_api_key: str, collection_name: str, milvus_host: str = "localhost", milvus_port: str = "19530"):
        """
        Temel retriever sınıfı
        
        Args:
            openai_api_key: OpenAI API anahtarı
            collection_name: Vector store koleksiyon adı
            milvus_host: Milvus sunucu adresi
            milvus_port: Milvus sunucu portu
        """
        self.openai_api_key = openai_api_key
        self.collection_name = collection_name
        self.milvus_host = milvus_host
        self.milvus_port = milvus_port
        
        # OpenAI embeddings oluştur
        try:
            self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        except Exception as e:
            print(f"Embeddings oluşturma hatası: {str(e)}")
            raise
        
        # Milvus bağlantısını oluştur
        try:
            connections.connect(
                alias="default", 
                host=milvus_host, 
                port=milvus_port
            )
        except Exception as e:
            print(f"Milvus bağlantı hatası: {str(e)}")
            raise
        
        # Milvus vector store oluştur/yükle
        try:
            self.vectorstore = Milvus(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                connection_args={"host": milvus_host, "port": milvus_port},
                vector_field="embedding"  # Bu satırı ekleyin - vektör alanının adını belirtiyor
            )
        except Exception as e:
            print(f"Vector store oluşturma hatası: {str(e)}")
            raise
        
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=openai_api_key,
            temperature=0
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        try:
            self.compressor = LLMChainExtractor.from_llm(self.llm)
        except Exception as e:
            print(f"Compressor oluşturma hatası: {str(e)}")
            self.compressor = None
        
        # Compression retriever oluştur
        if self.compressor:
            self.retriever = ContextualCompressionRetriever(
                base_compressor=self.compressor,
                base_retriever=self.vectorstore.as_retriever(
                    search_kwargs={"k": 5}
                )
            )
        else:
            # Compressor oluşturulamadıysa, normal retriever kullan
            self.retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 5}
            )
        
        self.query_prefix = ""
    
    async def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Sorguya göre ilgili dökümanları getirir
        
        Args:
            query: Kullanıcı sorusu
            
        Returns:
            List[Document]: İlgili dökümanların listesi
        """
        # Retriever'ın doğru şekilde yapılandırıldığından emin ol
        if not self.retriever:
            self._configure_retriever()
            
        prefixed_query = f"{self.query_prefix} {query}" if self.query_prefix else query
        
        try:
            return await self.retriever.aget_relevant_documents(prefixed_query)
        except Exception as e:
            print(f"Döküman getirme hatası: {str(e)}")
            # Hata durumunda boş liste dön
            return []
    
    def _configure_retriever(self) -> None:
        """
        Retriever'ı yeniden yapılandırır (örneğin bağlantı kaybolduğunda)
        """
        self.retriever = ContextualCompressionRetriever(
            base_compressor=self.compressor,
            base_retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 5}
            )
        )
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Vector store'a yeni dökümanlar ekler
        
        Args:
            documents: Eklenecek dökümanlar listesi
        """
        self.vectorstore.add_documents(documents)
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Vector store'a textler metinler ekler
        
        Args:
            texts: Eklenecek text listesi
            metadatas: Metinlerle ilişkilendirilecek metadata listesi
            
        Returns:
            List[str]: Eklenen dökümanların ID'leri
        """
        return self.vectorstore.add_texts(texts, metadatas)
    
    def load_documents(self, file_path: str, file_type: str = "text") -> List[Document]:
        """
        Belirtilen dosyadan dökümanları yükler ve bölümlendirir
        
        Args:
            file_path: Yüklenecek dosyanın yolu
            file_type: Dosya tipi ('text', 'pdf', 'csv')
            
        Returns:
            List[Document]: Yüklenen ve bölümlendirilen dökümanlar
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
        
        # Dosya tipine göre uygun yükleyici seç
        if file_type.lower() == "text":
            loader = TextLoader(file_path, encoding="utf-8")
        elif file_type.lower() == "pdf":
            loader = PyPDFLoader(file_path)
        elif file_type.lower() == "csv":
            loader = CSVLoader(file_path)
        else:
            raise ValueError(f"Desteklenmeyen dosya tipi: {file_type}")
        
        # Dökümanları yükle
        documents = loader.load()
        
        # Dökümanları split yap
        split_documents = self.text_splitter.split_documents(documents)
        
        return split_documents
    
    def add_file(self, file_path: str, file_type: str = "text") -> int:
        """
        Belirtilen dosyayı yükler, split yap ve vector store'a ekler
        
        Args:
            file_path: Yüklenecek dosyanın yolu
            file_type: Dosya tipi ('text', 'pdf', 'csv')
            
        Returns:
            int: Eklenen döküman sayısı
        """
        documents = self.load_documents(file_path, file_type)
        self.add_documents(documents)
        return len(documents)
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Koleksiyon statslarını döndürür
        
        Returns:
            Dict: Koleksiyon statsları
        """
        try:
            # Milvus'a bağlan
            connections.connect(
                alias="default", 
                host=self.milvus_host, 
                port=self.milvus_port
            )
            
            # Koleksiyonu kontrol et
            if not utility.has_collection(self.collection_name):
                return {
                    "collection_name": self.collection_name,
                    "document_count": 0,
                    "embedding_function": str(self.embeddings.__class__.__name__),
                    "status": "not_found"
                }
                
            # Koleksiyon istatistiklerini al
            collection = Collection(name=self.collection_name)
            collection.load()
            stats = {
                "collection_name": self.collection_name,
                "document_count": collection.num_entities,
                "embedding_function": str(self.embeddings.__class__.__name__),
                "status": "loaded"
            }
            collection.release()
            return stats
            
        except Exception as e:
            print(f"İstatistik alma hatası: {str(e)}")
            return {
                "collection_name": self.collection_name,
                "error": str(e)
            }


class GuidanceRetriever(BaseRetriever):
    def __init__(self, openai_api_key: str, milvus_host: str = "localhost", milvus_port: str = "19530"):
        """
        Rehberlik konusunda özelleşmiş retriever
        
        Args:
            openai_api_key: OpenAI API anahtarı
            milvus_host: Milvus sunucu adresi
            milvus_port: Milvus sunucu portu
        """
        super().__init__(openai_api_key, "rehberlik_collection", milvus_host, milvus_port)
        
        # Rehberlik için özel yapılandırmalar
        self.query_prefix = "Eğitim ve kariyer rehberliği konusunda"
        
        # Güncel LangChain sürümü için compressor oluşturma
        try:
            # 1. Yöntem: Basit compressor kullanma
            self.compressor = LLMChainExtractor.from_llm(self.llm)
        except Exception as e:
            print(f"Compressor oluşturma hatası: {str(e)}")
            # Fallback: Compressor olmadan devam et
            self.compressor = None
        
        # Özel retriever yapılandırması
        self.retriever = ContextualCompressionRetriever(
            base_compressor=self.compressor,
            base_retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 5}
            )
        ) if self.compressor else self.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )
    
    async def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Rehberlik odaklı sorguya göre ilgili dökümanları getirir
        
        Args:
            query: Kullanıcı sorusu
            
        Returns:
            List[Document]: İlgili rehberlik dökümanlarının listesi
        """
        # Rehberlik için sorguyu zenginleştir
        guidance_query = f"Eğitim ve kariyer rehberliği: {query}"
        return await super().get_relevant_documents(guidance_query)


class RecommendationRetriever():
    def __init__(self, postgre_url: str):
        """
        PostgreSQL tabanlı öneri retriever
        Args:
            postgre_url: postgresql://user:pass@host:port/dbname
        """
        self.postgre_url = postgre_url

    async def get_relevant_documents(self, topic: str, kind: str) -> List[Document]:
        print(topic, kind)
        topic = topic.strip().lower()
        kind = kind.strip().lower()
        documents = []

        try:
            conn = psycopg2.connect(self.postgre_url, options='-c client_encoding=LATIN5')
            with conn:
                conn.set_client_encoding("LATIN5")
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT topic, kind, context, description
                        FROM kaynaklar
                        WHERE topic = %s AND kind = %s
                        ORDER BY id ASC;
                    """, (topic, kind))

                    rows = cur.fetchall()
                    print(rows)
                    for row in rows:
                        topic, kind, context, _ = row
                        content = f"[{kind}] {context}"
                        documents.append(Document(page_content=content, metadata={"topic": topic}))
        except Exception as e:
            print(f"[ERROR] DB query failed: {e}")
    
        return documents

class MotivationRetriever(BaseRetriever):
    def __init__(self, openai_api_key: str, milvus_host: str = "localhost", milvus_port: str = "19530"):
        """
        Motivasyon konusunda özelleşmiş retriever
        
        Args:
            openai_api_key: OpenAI API anahtarı
            milvus_host: Milvus sunucu adresi
            milvus_port: Milvus sunucu portu
        """
        super().__init__(openai_api_key, "motivasyon_collection", milvus_host, milvus_port)
        
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=openai_api_key,
            temperature=0.05
        )
        
        try:
            self.compressor = LLMChainExtractor.from_llm(self.llm)
        except Exception as e:
            print(f"Compressor oluşturma hatası: {str(e)}")
            self.compressor = None
        
        # Retriever yapılandırması 
        if self.compressor:
            self.retriever = ContextualCompressionRetriever(
                base_compressor=self.compressor,
                base_retriever=self.vectorstore.as_retriever(
                    search_kwargs={"k": 5}  
                )
            )
        else:
            self.retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 5}
            )
    
    async def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Motivasyon odaklı sorguya göre ilgili dökümanları getirir
        
        Args:
            query: Kullanıcı sorusu
            
        Returns:
            List[Document]: İlgili motivasyon dökümanlarının listesi
        """
        motivational_query = f"Motivasyon ve ilham: {query}"
        return await super().get_relevant_documents(motivational_query)
    

class CoachRetriever(BaseRetriever):
    def __init__(self, openai_api_key: str, milvus_host: str = "localhost", milvus_port: str = "19530"):
        """
        Koç profilleri için özelleşmiş retriever
        
        Args:
            openai_api_key: OpenAI API anahtarı
            milvus_host: Milvus sunucu adresi
            milvus_port: Milvus sunucu portu
        """
        super().__init__(openai_api_key, "koc_collection", milvus_host, milvus_port)
        
        # Koç araması için özel yapılandırmalar
        self.query_prefix = "Öğrenciye uygun koç önerisi"
        
        # OpenAI modeli
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=openai_api_key,
            temperature=0.2
        )
        
        # Milvus ile doğrudan etkileşimler için
        from pymilvus import connections, Collection
    
    async def search_coaches(self, query_text, filters=None, top_k=3):
        """
        Koç araması yapar
        
        Args:
            query_text: Öğrenci sorgusu
            filters: Koç araması için filtreler
            top_k: Kaç koç döndürüleceği
            
        Returns:
            List: Koç arama sonuçları
        """
        from pymilvus import connections, Collection
        
        # Önce Milvus'a bağlan
        connections.connect(
            alias="default", 
            host=self.milvus_host, 
            port=self.milvus_port
        )
        
        # Sorgu embeddingi oluştur
        query_embedding = self.embeddings.embed_query(query_text)
        
        # Filtreleme ifadesini oluştur
        expr = None
        if filters:
            conditions = []
            
            # Temel filtreler
            if "kocluk_ucreti" in filters:
                min_ucret = filters["kocluk_ucreti"].get("min", 0)
                max_ucret = filters["kocluk_ucreti"].get("max", 100000)
                conditions.append(f"kocluk_ucreti >= {min_ucret} and kocluk_ucreti <= {max_ucret}")
            
            if "tecrube_sene" in filters:
                min_tecrube = filters["tecrube_sene"].get("min", 0)
                conditions.append(f"tecrube_sene >= {min_tecrube}")
            
            if "mezuna_kaldi" in filters:
                mezuna_kaldi_val = "true" if filters["mezuna_kaldi"] else "false"
                conditions.append(f"mezuna_kaldi == {mezuna_kaldi_val}")
            
            if "mezun_ogrenci_kabul" in filters:
                mezun_kabul_val = "true" if filters["mezun_ogrenci_kabul"] else "false"
                conditions.append(f"mezun_ogrenci_kabul == {mezun_kabul_val}")
            
            if "alt_sinif_kabul" in filters:
                alt_sinif_val = "true" if filters["alt_sinif_kabul"] else "false"
                conditions.append(f"alt_sinif_kabul == {alt_sinif_val}")
            
            # Derece filtrelemeleri
            if "tyt_derece_son" in filters:
                max_tyt = filters["tyt_derece_son"].get("max", 100000)
                if max_tyt > 0:
                    conditions.append(f"tyt_derece_son > 0 and tyt_derece_son <= {max_tyt}")
            
            if "sayisal_derece_son" in filters:
                max_sayisal = filters["sayisal_derece_son"].get("max", 100000)
                if max_sayisal > 0:
                    conditions.append(f"sayisal_derece_son > 0 and sayisal_derece_son <= {max_sayisal}")
            
            if conditions:
                expr = " and ".join(conditions)
        
        # Koleksiyonu hazırla
        collection = Collection(name="koc_collection")
        collection.load()
        
        # Arama yap
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        try:
            results = collection.search(
                data=[query_embedding], 
                anns_field="embedding", 
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=[
                    "isim_soyisim", "okul", "bolum", "biyografi", "kocluk_ucreti", 
                    "tecrube_sene", "mezuna_kaldi", "mezun_ogrenci_kabul", 
                    "alt_sinif_kabul", "kocluk_alani", "guclu_alanlar", 
                    "tyt_derece_ilk", "sayisal_derece_ilk", "sozel_derece_ilk", "ea_derece_ilk", "dil_derece_ilk",
                    "tyt_derece_son", "sayisal_derece_son", "sozel_derece_son", "ea_derece_son"
                ]
            )
            return results
        except Exception as e:
            print(f"Koç arama hatası: {str(e)}")
            return None
        finally:
            collection.release()
    
    async def analyze_student_needs(self, query: str):
        """
        Öğrenci sorgusunu analiz ederek uygun filtreleri belirler
        
        Args:
            query: Öğrenci sorusu
            
        Returns:
            Dict: Uygun filtreler
        """
        try:
            # Direkt olarak chain oluştur
            from langchain.chains import LLMChain
            from langchain.prompts import PromptTemplate
            
            template = """
            Sen bir eğitim koçu eşleştirme uzmanısın. 
            
            Aşağıda bir öğrencinin mesajı verilmiştir. Bu mesajı analiz ederek öğrenciye uygun koç filtreleri belirle.
            
            Öğrenci Mesajı: {query}
            
            Şu filtreler belirlenebilir:
            1. Koçluk alanı (sayısal, sözel, eşit ağırlık, dil)
            2. Koçun mezuna kalıp kalmadığı (mezuna_kaldi: true/false)
            3. Öğrencinin sınıf seviyesi (mezun_ogrenci_kabul veya alt_sinif_kabul)
            4. Koçun tecrübe seviyesi (minimum tecrübe senesi)
            5. Maksimum koçluk ücreti
            6. Koçun başarı derecesi (sayısal, sözel, eşit ağırlık, TYT)
            
            JSON formatında filtreler oluştur. Sadece öğrencinin mesajında açıkça belirtilen veya çıkarılabilecek filtreleri dahil et.
            Örnek format:
            {{
                "kocluk_alani": ["sayısal"],
                "mezuna_kaldi": true,
                "mezun_ogrenci_kabul": true,
                "tecrube_sene": {{"min": 1}},
                "kocluk_ucreti": {{"max": 3000}},
                "sayisal_derece_son": {{"max": 5000}}
            }}
            
            Sadece JSON döndür, başka açıklama yapma.
            """
            
            prompt = PromptTemplate(template=template, input_variables=["query"])
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Chain'i çalıştır
            filters_text = await chain.arun(query=query)
            
            # JSON'ı ayıkla
            import json
            import re
            
            # Yanıtı temizle
            filters_text = filters_text.strip()
            
            # Doğrudan JSON olarak parse etmeyi dene
            try:
                filters = json.loads(filters_text)
                return filters
            except json.JSONDecodeError:
                # JSON bloğunu bul
                json_match = re.search(r'({.*})', filters_text, re.DOTALL)
                if json_match:
                    filters_json = json_match.group(1)
                    try:
                        filters = json.loads(filters_json)
                        return filters
                    except json.JSONDecodeError:
                        print(f"Geçerli JSON formatı bulunamadı: {filters_json}")
                        return {}
                else:
                    print(f"JSON formatı bulunamadı, ham yanıt: {filters_text}")
                    return {}
        except Exception as e:
            print(f"Filtre analiz hatası: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {}
