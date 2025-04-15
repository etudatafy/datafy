# document_processor.py
import os
import asyncio
from typing import List, Dict, Any, Optional
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Milvus
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from pymilvus import connections, utility, Collection, FieldSchema, CollectionSchema, DataType
import os
import uuid
import asyncio
import numpy as np
from typing import List, Dict, Any, Optional
from langchain.embeddings import OpenAIEmbeddings
from pymilvus import connections, utility, Collection, FieldSchema, CollectionSchema, DataType
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class DocumentService:
    """
    Döküman işleme servislerini yöneten sınıf
    """
    def __init__(self, openai_api_key: str, milvus_host: str = "localhost", milvus_port: str = "19530"):
        self.openai_api_key = openai_api_key
        self.milvus_host = milvus_host
        self.milvus_port = milvus_port
        
        # Langchain'in PDFProcessor'ı yerine direct Milvus işleyici kullan
        self.pdf_processor = DirectMilvusPDFProcessor(openai_api_key, milvus_host, milvus_port)
        
        # Desteklenen koleksiyonları Milvus'tan yükle
        self.collections = {}
        self._load_collections_from_milvus()
    
    def _load_collections_from_milvus(self):
        """
        Milvus'taki mevcut koleksiyonları yükler
        """
        try:
            # Milvus'a bağlan
            connections.connect(
                alias="default", 
                host=self.milvus_host, 
                port=self.milvus_port
            )
            
            # Tüm koleksiyonları listele
            milvus_collections = utility.list_collections()
            
            # Koleksiyonları işle
            for collection_name in milvus_collections:
                # "_collection" ile biten koleksiyonlar için
                if collection_name.endswith("_collection"):
                    friendly_name = collection_name.replace("_collection", "")
                    
                    if friendly_name.endswith("_collection"):
                        friendly_name = friendly_name.replace("_collection", "")
                        print(f"Uyarı: Çift '_collection' eki tespit edildi: {collection_name}")
                    
                    self.collections[friendly_name] = collection_name
                else:
                    self.collections[collection_name] = collection_name
            
            print(f"Milvus'tan {len(self.collections)} koleksiyon yüklendi: {self.collections}")
        except Exception as e:
            print(f"Milvus'tan koleksiyon yükleme hatası: {str(e)}")
    
    async def process_document(self, document_url: str, collection_name: str, document_type: str) -> Dict[str, Any]:
        """
        Belirtilen dökümanı işler
        
        Args:
            document_url: Döküman URL'si veya dosya yolu
            collection_name: İçeriği eklenecek koleksiyon adı
            document_type: Döküman tipi (şu an sadece 'pdf' desteklenir)
            
        Returns:
            Dict: İşlem sonucu
        """
        print(f"Döküman işleme talebi: {document_url}, tip: {document_type}, koleksiyon: {collection_name}")
        
        # Koleksiyon adını kontrol et
        vector_collection = None
        
        # Koleksiyon ismi zaten varsa kullan
        if collection_name in self.collections:
            vector_collection = self.collections[collection_name]
            print(f"Var olan koleksiyon kullanılıyor: {collection_name} -> {vector_collection}")
        else:
            # Yeni bir koleksiyon oluştur
            new_vector_collection = f"{collection_name}_collection"
            print(f"Yeni koleksiyon oluşturuluyor: {collection_name} -> {new_vector_collection}")
            
            # Koleksiyonu oluştur ve kaydet
            self.collections[collection_name] = new_vector_collection
            vector_collection = new_vector_collection
        
        # Döküman tipine göre işleme yap - sadece pdf işleme var şu anda
        if document_type.lower() == "pdf":
            return await self.pdf_processor.process_pdf(document_url, vector_collection)
        else:
            return {
                "success": False,
                "message": f"Desteklenmeyen döküman tipi: {document_type}. Şu an sadece PDF desteklenmektedir.",
                "document_count": 0
            }
    
    async def get_all_collections(self) -> Dict[str, Any]:
        """
        Hem tanımlı koleksiyonları hem de vector store'daki gerçek koleksiyonları döndürür
        
        Returns:
            Dict: Koleksiyon bilgileri
        """
        try:
            # Milvus'a bağlan
            connections.connect(
                alias="default", 
                host=self.milvus_host, 
                port=self.milvus_port
            )
            
            # Tüm koleksiyonları listele
            db_collections = utility.list_collections()
            
            # Koleksiyon istatistiklerini al
            collection_stats = []
            for col_name in db_collections:
                try:
                    collection = Collection(name=col_name)
                    collection.load()
                    count = collection.num_entities
                    collection_stats.append({
                        "name": col_name,
                        "count": count
                    })
                    collection.release()
                except Exception as e:
                    collection_stats.append({
                        "name": col_name,
                        "count": "Error: " + str(e)
                    })
            
            # Tanımlı koleksiyonları ve gerçek koleksiyonları döndür
            return {
                "defined_collections": list(self.collections.keys()),
                "actual_collections": collection_stats,
                "error": None
            }
        except Exception as e:
            return {
                "defined_collections": list(self.collections.keys()),
                "actual_collections": [],
                "error": str(e)
            }
    
    async def clean_and_recreate_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Mevcut koleksiyonu temizler ve yeniden oluşturur
        
        Args:
            collection_name: Koleksiyon adı
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # Milvus'a bağlan
            connections.connect(
                alias="default", 
                host=self.milvus_host, 
                port=self.milvus_port
            )
            
            # Koleksiyon var mı kontrol et
            if utility.has_collection(collection_name):
                print(f"Koleksiyon siliniyor: {collection_name}")
                utility.drop_collection(collection_name)
            
            # Yeni koleksiyon oluştur
            self.pdf_processor.ensure_collection_exists(collection_name)
            
            return {
                "success": True,
                "message": f"Koleksiyon '{collection_name}' başarıyla temizlendi ve yeniden oluşturuldu"
            }
        except Exception as e:
            print(f"Koleksiyon temizleme hatası: {str(e)}")
            return {
                "success": False,
                "message": f"Koleksiyon temizlerken hata oluştu: {str(e)}"
            }

    async def create_collection(self, collection_name: str, collection_description: str = "") -> Dict[str, Any]:
        """
        Yeni bir koleksiyon oluşturur
        """
        # Koleksiyon adı kontrolü
        if not collection_name or not collection_name.strip():
            return {
                "success": False,
                "message": "Geçersiz koleksiyon adı"
            }
        
        # Boşlukları alt çizgi ile değiştir ve küçük harfe çevir
        collection_name = collection_name.strip().lower().replace(" ", "_")
        
        # "_collection" ile bitiyorsa kaldır (çift "_collection" oluşmasını engeller)
        if collection_name.endswith("_collection"):
            collection_name = collection_name[:-11]  # "_collection" uzunluğunu çıkar
        
        # Koleksiyon zaten var mı kontrol et
        if collection_name in self.collections:
            vector_collection = self.collections[collection_name]
            return {
                "success": True,
                "message": f"'{collection_name}' koleksiyonu zaten tanımlı ({vector_collection})",
                "collection_name": collection_name,
                "vector_store_name": vector_collection
            }
        
        vector_store_name = f"{collection_name}_collection"
        
        try:
            # Direct processor kullanarak koleksiyonu oluştur
            if self.pdf_processor.ensure_collection_exists(vector_store_name):
                # Koleksiyonu tanım listesine ekle
                self.collections[collection_name] = vector_store_name
                
                return {
                    "success": True,
                    "message": f"'{collection_name}' koleksiyonu başarıyla oluşturuldu",
                    "collection_name": collection_name,
                    "vector_store_name": vector_store_name
                }
            else:
                return {
                    "success": False,
                    "message": f"Koleksiyon oluşturulamadı: {vector_store_name}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Koleksiyon oluşturulurken hata: {str(e)}"
            }
    
    async def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Bir koleksiyonu siler
        
        Args:
            collection_name: Silinecek koleksiyon adı
            
        Returns:
            Dict: İşlem sonucu
        """
        # Koleksiyon tanımlı mı kontrol et
        if collection_name not in self.collections:
            return {
                "success": False,
                "message": f"'{collection_name}' koleksiyonu bulunamadı"
            }
        
        vector_store_name = self.collections[collection_name]
        
        try:
            # Milvus'a bağlan
            connections.connect(
                alias="default", 
                host=self.milvus_host, 
                port=self.milvus_port
            )
            
            # Koleksiyon var mı kontrol et
            if not utility.has_collection(vector_store_name):
                del self.collections[collection_name]
                return {
                    "success": True,
                    "message": f"'{collection_name}' koleksiyonu tanımı silindi (vector store zaten yoktu)"
                }
            
            # Koleksiyonu sil
            utility.drop_collection(vector_store_name)
            
            # Koleksiyonu tanım listesinden çıkar
            del self.collections[collection_name]
            
            return {
                "success": True,
                "message": f"'{collection_name}' koleksiyonu ve ilişkili tüm veriler başarıyla silindi"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Koleksiyon silinirken hata: {str(e)}"
            }

class DirectMilvusPDFProcessor:
    """
    Langchain Milvus entegrasyonunu atlamak için doğrudan Milvus API'sini kullanarak PDF dosyalarını işler
    """
    def __init__(self, openai_api_key: str, milvus_host: str = "localhost", milvus_port: str = "19530"):
        self.openai_api_key = openai_api_key
        self.milvus_host = milvus_host
        self.milvus_port = milvus_port
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self._connect_to_milvus()
    
    def _connect_to_milvus(self):
        try:
            connections.connect(
                alias="default", 
                host=self.milvus_host, 
                port=self.milvus_port
            )
            print(f"Milvus bağlantısı başarılı: {self.milvus_host}:{self.milvus_port}")
        except Exception as e:
            print(f"Milvus bağlantı hatası: {str(e)}")
            raise
    
    def get_collection_schema(self, collection_name):
        """
        Var olan bir koleksiyonun şemasını getirir
        """
        try:
            if not utility.has_collection(collection_name):
                return None
                
            collection = Collection(name=collection_name)
            schema = collection.schema
            return schema
        except Exception as e:
            print(f"Koleksiyon şeması alınamadı: {str(e)}")
            return None
    
    def ensure_collection_exists(self, collection_name: str) -> bool:
        """
        Koleksiyonun varlığını kontrol eder, yoksa oluşturur
        
        Args:
            collection_name: Koleksiyon adı
            
        Returns:
            bool: Başarılı olup olmadığı
        """
        try:
            self._connect_to_milvus()  # Bağlantıyı yenile
            
            if utility.has_collection(collection_name):
                print(f"Koleksiyon zaten mevcut: {collection_name}")
                return True
            
            # Koleksiyon yoksa oluştur
            print(f"Koleksiyon oluşturuluyor: {collection_name}")
            
            # Koleksiyon şeması
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="metadata", dtype=DataType.JSON),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)  # OpenAI embeddings
            ]
            schema = CollectionSchema(fields=fields, description=f"PDF içerikleri için koleksiyon: {collection_name}")
            
            # Koleksiyonu oluştur
            collection = Collection(name=collection_name, schema=schema)
            
            index_params = {
                "index_type": "HNSW",
                "metric_type": "COSINE",
                "params": {"M": 8, "efConstruction": 64}
            }
            collection.create_index(field_name="embedding", index_params=index_params)
            print(f"Koleksiyon ve indeks başarıyla oluşturuldu: {collection_name}")
            
            return True
        except Exception as e:
            print(f"Koleksiyon oluşturma hatası: {str(e)}")
            return False
    
    async def process_pdf(self, file_path: str, collection_name: str) -> Dict[str, Any]:
        """
        PDF dosyasını okur, parçalara böler, embeddings oluşturur ve Milvus'a ekler
        
        Args:
            file_path: PDF dosya yolu
            collection_name: Milvus koleksiyon adı
            
        Returns:
            Dict: İşlem sonucu
        """
        try:
            # Dosyayı kontrol et
            if not os.path.exists(file_path):
                return {"success": False, "message": f"Dosya bulunamadı: {file_path}", "document_count": 0}
            
            print(f"PDF işleniyor: {file_path} -> {collection_name}")
            
            # Koleksiyon varlığını kontrol et
            if not self.ensure_collection_exists(collection_name):
                return {"success": False, "message": f"Koleksiyon oluşturulamadı: {collection_name}", "document_count": 0}
            
            # Koleksiyon şemasını al
            schema = self.get_collection_schema(collection_name)
            if not schema:
                return {"success": False, "message": f"Koleksiyon şeması alınamadı: {collection_name}", "document_count": 0}
            
            # Metadata alanının tipini öğren
            metadata_field = None
            field_type = None
            for field in schema.fields:
                if field.name == "metadata":
                    metadata_field = field
                    field_type = field.dtype
                    break
            
            print(f"Metadata alanı tipi: {field_type}")
            
            # Text parçalarını çıkar
            text_chunks = self._extract_text_from_pdf(file_path)
            
            if not text_chunks:
                return {"success": False, "message": "PDF'den metin çıkarılamadı", "document_count": 0}
            
            print(f"PDF'den {len(text_chunks)} metin parçası çıkarıldı")
            
            # Her bir text parçası için embeddings oluştur
            successful_chunks = 0
            
            # Koleksiyonu al
            collection = Collection(name=collection_name)
            
            # Toplu veri hazırla
            entity_ids = []
            texts = []
            metadatas = []
            embeddings_list = []
            
            batch_size = 10
            for i in range(0, len(text_chunks), batch_size):
                batch_chunks = text_chunks[i:i+batch_size]
                
                try:
                    # Her birisi için embedding oluştur
                    for idx, chunk in enumerate(batch_chunks):
                        chunk_idx = i + idx
                        
                        # Boş veya çok kısa metinleri atla
                        if not chunk or len(chunk.strip()) < 20:
                            print(f"Parça {chunk_idx+1} çok kısa, atlanıyor")
                            continue
                        
                        # Verileri hazırla
                        doc_id = f"{collection_name}_{uuid.uuid4()}"
                        
                        # Metadata tipine göre uygun şekilde ekle
                        if field_type == DataType.JSON:
                            metadata = {
                                "source": file_path,
                                "index": chunk_idx
                            }
                        else:
                            metadata = f"source: {file_path}, index: {chunk_idx}"
                        
                        entity_ids.append(doc_id)
                        texts.append(chunk)
                        metadatas.append(metadata)
                    
                    # Tüm batch için bir kerede embeddings oluştur
                    if texts:
                        print(f"Batch embeddings oluşturuluyor ({len(texts)} parça)...")
                        batch_embeddings = await self._get_embeddings_async(texts)
                        embeddings_list.extend(batch_embeddings)
                        
                        if entity_ids and texts and metadatas and embeddings_list:
                            print(f"Milvus'a {len(entity_ids)} parça ekleniyor...")
                            
                            entities = [
                                entity_ids,
                                texts,
                                metadatas,
                                embeddings_list
                            ]
                            
                            # Veriyi koleksiyona ekle
                            insert_result = collection.insert(entities)
                            successful_chunks += len(entity_ids)
                            
                            print(f"Batch ekleme başarılı: {insert_result}")
                            
                        # Listeleri temizle
                        entity_ids = []
                        texts = []
                        metadatas = []
                        embeddings_list = []
                
                except Exception as batch_error:
                    print(f"Batch işleme hatası: {str(batch_error)}")
            
            # Sonuçları bildir
            if successful_chunks > 0:
                return {
                    "success": True,
                    "message": f"PDF başarıyla işlendi: {successful_chunks} metin parçası eklendi",
                    "document_count": successful_chunks
                }
            else:
                return {
                    "success": False,
                    "message": "PDF işlendi ancak hiç metin parçası eklenemedi",
                    "document_count": 0
                }
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"PDF işleme genel hatası:\n{error_trace}")
            return {"success": False, "message": f"PDF işleme hatası: {str(e)}", "document_count": 0}

    def create_temp_pdf_from_text(self, text: str) -> str:
        """
        Creates a temporary PDF file containing the provided text.
        
        Args:
            text: The text content to include in the PDF.
        
        Returns:
            The file path of the created temporary PDF.
        """
        # Create a temporary file with a .pdf suffix (it won't be auto-deleted)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            output_path = tmp.name

        # Create a canvas for the PDF using the letter page size
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        margin = 40
        x = margin
        y = height - margin
        line_height = 14  # Adjust this value to change line spacing

        # Split the text into lines and write them to the PDF
        for line in text.split("\n"):
            c.drawString(x, y, line)
            y -= line_height
            # If we reach the bottom margin, start a new page
            if y < margin:
                c.showPage()
                y = height - margin

        # Finalize the PDF file
        c.save()
        return output_path
        
    async def process_pdf_by_page_lists(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"success": False, "message": f"Dosya bulunamadı: {file_path}"}

        print(f"PDF işleniyor (sayfa listeleri ile bölümlere ayrılacak): {file_path}")

        try:
            from pypdf import PdfReader
        except ImportError:
            return {"success": False, "message": "pypdf modülü yüklü değil."}

        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        print(f"Toplam sayfa: {total_pages}")

        # 🔁 Define your custom page lists here
        sections = {
            "rehberlik": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
            "öneri": list(range(21, 50)),  # Fill this later
            "motivasyon": []  # Fill this later
        }

        results = {}

        for section, page_list in sections.items():
            if not page_list:
                results[section] = {"success": False, "message": "Sayfa listesi tanımlanmadı."}
                continue

            # Filter invalid pages
            valid_pages = [p for p in page_list if 1 <= p <= total_pages]
            if not valid_pages:
                results[section] = {"success": False, "message": f"{section} için geçerli sayfa bulunamadı."}
                continue

            print(f"{section} bölümü için sayfalar: {valid_pages}")

            # Read and collect text
            text_chunks = []
            for p in valid_pages:
                try:
                    text = reader.pages[p - 1].extract_text()
                    if text and text.strip():
                        text_chunks.append(text.strip())
                except Exception as e:
                    print(f"Sayfa {p} okunamadı: {str(e)}")

            if not text_chunks:
                results[section] = {"success": False, "message": f"{section} metni boş"}
                continue

            # Write to temporary file
            section_text = "\n\n".join(text_chunks)
            temp_path = self.create_temp_pdf_from_text(section_text)

            # Process as PDF
            result = await self.process_pdf(temp_path, section)
            results[section] = result

            os.remove(temp_path)

        return {
            "success": True,
            "message": "PDF özel sayfa listeleriyle işlendi",
            "results": results
        }
    
    def _extract_text_from_pdf(self, file_path: str) -> List[str]:
        """
        PDF'den metin çıkarır
        
        Args:
            file_path: PDF dosya yolu
            
        Returns:
            List[str]: Metin parçaları
        """
        text_chunks = []
        
        # İlk yöntem: PyPDF
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            
            for i, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        cleaned_text = text.strip()
                        text_chunks.append(cleaned_text)
                except Exception as e:
                    print(f"Sayfa {i+1} okuma hatası: {str(e)}")
        
        except Exception as e:
            print(f"PyPDF okuma hatası: {str(e)}")
            
            # İkinci yöntem: PDFMiner
            try:
                from pdfminer.high_level import extract_text
                text = extract_text(file_path)
                
                if text:
                    paragraphs = text.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            text_chunks.append(para.strip())
            except Exception as pdf_miner_error:
                print(f"PDFMiner okuma hatası: {str(pdf_miner_error)}")
        
        if text_chunks:
            try:
                # Önce document formatına dönüştür
                documents = [Document(page_content=chunk) for chunk in text_chunks]
                # Parçala
                split_docs = self.text_splitter.split_documents(documents)
                # Metin olarak geri al
                return [doc.page_content for doc in split_docs]
            except Exception as split_error:
                print(f"Metin parçalama hatası: {str(split_error)}")
                return text_chunks
        else:
            return []
    
    async def _get_embeddings_async(self, texts: List[str]) -> List[List[float]]:
        """
        Metinler için eşzamanlı embeddings oluşturur
        
        Args:
            texts: Metin listesi
            
        Returns:
            List[List[float]]: Embeddings listesi
        """
        try:
            # OpenAI embeddings
            embeddings = await self.embeddings.aembed_documents(texts)
            return embeddings
        except Exception as e:
            print(f"Embeddings oluşturma hatası: {str(e)}")
            return [[0.0] * 1536 for _ in range(len(texts))]