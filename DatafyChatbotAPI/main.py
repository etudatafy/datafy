from fastapi import FastAPI, Depends, HTTPException, Header, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi.responses import RedirectResponse
from typing import Dict, List, Optional, Any
import os
import asyncio
import uvicorn
import shutil
import uuid
from dotenv import load_dotenv
from modules.agent import EducationAgentSystem
from modules.document_processor import DocumentService
from pymilvus import connections


# .env dosyasını yükle
load_dotenv()

app = FastAPI(
    title="Destek AL Chatbot API",
    description="RAG tabanlı eğitim asistanı sistemine erişim için API",
    version="1.0.0"
)

# CORS ayarları 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm kaynaklara izin veriyoruz (bunu production'da düzeltmemiz lazım)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
POSTGRE_URL = os.getenv("POSTGRE_URL", "postgresql://postgres:password@localhost:5432/postgres")

if not OPENAI_API_KEY:
    print("UYARI: OPENAI_API_KEY bulunamadı. Lütfen .env dosyasını kontrol edin.")

# Sistem başlatma ve önbelleğe alma
agent_systems = {}
document_service = None

# Geçici dosyaların saklanacağı dizin
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# İşlem statusleri için basit bir depo
task_statuses = {}

async def get_agent_system(user_id: str):
    """
    Kullanıcı ID'sine göre agent sistemi döndürür veya oluşturur
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API anahtarı yapılandırılmamış")
    
    if user_id not in agent_systems:
        agent_systems[user_id] = EducationAgentSystem(OPENAI_API_KEY, MILVUS_HOST, MILVUS_PORT)
    
    return agent_systems[user_id]

async def get_document_service():
    """
    Document service nesnesini döndürür
    """
    global document_service
    
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API anahtarı yapılandırılmamış")
    
    if document_service is None:
        document_service = DocumentService(OPENAI_API_KEY, MILVUS_HOST, MILVUS_PORT)
    
    return document_service


# Modeller
class QueryRequest(BaseModel):
    query: str = Field(..., description="Kullanıcının sorusu veya isteği", example="Matematik sınavına nasıl hazırlanmalıyım?")
    user_id: str = Field(..., description="Kullanıcı kimlik bilgisi", example="user_123")


class QueryResponse(BaseModel):
    agent: str = Field(..., description="Yanıtı üreten ajanın türü", example="rehberlik")
    response: str = Field(..., description="Ajanın ürettiği yanıt")


class DocumentUploadRequest(BaseModel):
    collection_name: str = Field(..., description="Dökümanın ekleneceği koleksiyon adı", example="rehberlik")
    document_url: str = Field(..., description="Dökümanın URL'si veya dosya yolu", example="/path/to/document.pdf")
    document_type: str = Field(..., description="Dökümanın tipi", example="pdf")


class DocumentUploadResponse(BaseModel):
    success: bool = Field(..., description="İşlem başarılı mı?")
    message: str = Field(..., description="İşlem hakkında bilgi")
    document_count: int = Field(..., description="Eklenen döküman sayısı")


class DocumentProcessingStatus(BaseModel):
    task_id: str = Field(..., description="İşlem ID'si")
    status: str = Field(..., description="İşlem durumu", example="processing")
    message: str = Field(..., description="Durum mesajı")


class CreateCollectionRequest(BaseModel):
    collection_name: str = Field(..., description="Oluşturulacak koleksiyon adı", example="matematik")
    description: str = Field("", description="Koleksiyon açıklaması", example="Matematik dersleri ile ilgili kaynaklar")


class DeleteCollectionRequest(BaseModel):
    collection_name: str = Field(..., description="Silinecek koleksiyon adı", example="matematik")


class CollectionInfo(BaseModel):
    defined_collections: List[str] = Field(..., description="Tanımlı koleksiyonlar")
    actual_collections: List[Dict[str, Any]] = Field(..., description="Vector store'daki koleksiyonlar")
    error: Optional[str] = Field(None, description="Hata mesajı (varsa)")


class CollectionActionResponse(BaseModel):
    success: bool = Field(..., description="İşlem başarılı mı?")
    message: str = Field(..., description="İşlem hakkında bilgi")
    collection_name: Optional[str] = Field(None, description="İşlem yapılan koleksiyon adı")
    vector_store_name: Optional[str] = Field(None, description="Vector store'daki karşılık gelen koleksiyon adı")


class ResetCollectionRequest(BaseModel):
    collection_name: str = Field(..., description="Sıfırlanacak koleksiyon adı", example="matematik")



# Yardımcı fonksiyonlar
async def handle_document_upload(service, document_url, collection_name, document_type):
    """
    Document yükleme işlemini arka planda gerçekleştirir
    """
    try:
        result = await service.process_document(document_url, collection_name, document_type)
        print(f"Döküman işleme tamamlandı: {result}")
    except Exception as e:
        print(f"Döküman işleme hatası: {str(e)}")


async def handle_file_upload(service, file_path, collection_name, task_id):
    """
    Yüklenen dosyayı işler ve durumunu günceller
    """
    try:
        # İşlem durumunu başlatıldı olarak işaretle
        task_statuses[task_id] = {
            "status": "processing",
            "message": "Döküman işleniyor..."
        }
        
        print(f"Dosya işleme başladı: {file_path}, koleksiyon: {collection_name}, task_id: {task_id}")
        
        # Dökümanı işle
        result = await service.process_document(file_path, collection_name, "pdf")
        
        # İşlem durumunu güncelle
        if result["success"]:
            task_statuses[task_id] = {
                "status": "completed",
                "message": result["message"],
                "document_count": result.get("document_count", 0)
            }
            print(f"Dosya işleme başarılı: {result['message']}")
        else:
            task_statuses[task_id] = {
                "status": "failed",
                "message": result["message"]
            }
            print(f"Dosya işleme başarısız: {result['message']}")
        
        # Geçici dosyayı temizle
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Geçici dosya silindi: {file_path}")
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Dosya işleme detaylı hata:\n{error_trace}")
        
        # Hata durumunda güncelle
        task_statuses[task_id] = {
            "status": "failed",
            "message": f"İşlem hatası: {str(e)}"
        }
        
        # Hata olsa bile geçici dosyayı temizlemeyi dene
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Hata sonrası geçici dosya silindi: {file_path}")
            except Exception as cleanup_error:
                print(f"Geçici dosya silinemedi: {str(cleanup_error)}")
                pass


# Endpointler
@app.post("/query", response_model=QueryResponse, tags=["Sorgu"])
async def process_query(request: QueryRequest):
    """
    Kullanıcı sorgusunu işler ve uygun ajandan yanıt döndürür
    """
    if request.user_id not in agent_systems:
        agent_systems[request.user_id] = EducationAgentSystem(
            OPENAI_API_KEY, MILVUS_HOST, MILVUS_PORT, POSTGRE_URL
        )
    
    agent_system = agent_systems[request.user_id]
    
    try:
        result = await agent_system.process_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sorgu işlenirken hata oluştu: {str(e)}")
    
# Bu endpoint gerekli mi değil mi emin değilim bunu kaldırabiliriz -Ayberk
@app.post("/documents/upload", response_model=DocumentUploadResponse, tags=["Döküman Yönetimi"])
async def upload_document(request: DocumentUploadRequest, background_tasks: BackgroundTasks):
    """
    URL'deki veya dosya sistemindeki dökümanı vector store'a ekler
    """
    service = await get_document_service()
    
    background_tasks.add_task(
        handle_document_upload,
        service,
        request.document_url,
        request.collection_name,
        request.document_type
    )
    
    return {
        "success": True,
        "message": f"Döküman işleme sıraya alındı: {request.document_url}",
        "document_count": 0  # İşlem başlatıldı ama henüz tamamlanmadı
    }

@app.post("/documents/upload/by-pages", tags=["Döküman Yönetimi"])
async def upload_document_by_pages(request: DocumentUploadRequest):
    """
    Belirtilen dosya yolundaki PDF dosyasını özel sayfa listeleriyle işler ve bölümlere göre koleksiyonlar oluşturur.
    """
    file_path = request.document_url
    
    # Check if the file exists at the given path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail=f"Dosya bulunamadı: {file_path}")
    
    service = await get_document_service()
    result = await service.pdf_processor.process_pdf_by_page_lists(file_path)
    
    return result

@app.post("/documents/upload/file", tags=["Döküman Yönetimi"])
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    collection_name: str = Form(...),
):
    """
    Dosyayı yükler ve vector store'a ekler
    """
    if not file.filename.lower().endswith('.pdf'):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Sadece PDF dosyaları desteklenmektedir",
                "document_count": 0
            }
        )
    
    # Dosyayı geçici bir konuma kaydet
    temp_file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Dosya kaydedilirken hata oluştu: {str(e)}",
                "document_count": 0
            }
        )
    
    # Dökümanı işleme başlat
    service = await get_document_service()
    task_id = str(uuid.uuid4())
    
    background_tasks.add_task(
        handle_file_upload,
        service,
        temp_file_path,
        collection_name,
        task_id
    )
    
    return {
        "success": True,
        "message": f"Dosya yüklendi ve işleme alındı: {file.filename}",
        "task_id": task_id
    }


@app.get("/documents/status/{task_id}", response_model=DocumentProcessingStatus, tags=["Döküman Yönetimi"])
async def get_document_status(task_id: str):
    """
    Döküman işleme durumunu kontrol eder
    """
    if task_id not in task_statuses:
        return {
            "task_id": task_id,
            "status": "unknown",
            "message": "Belirtilen işlem ID'si bulunamadı"
        }
    
    status_info = task_statuses[task_id]
    return {
        "task_id": task_id,
        "status": status_info["status"],
        "message": status_info["message"]
    }


@app.get("/agents", response_model=List[str], tags=["Sistem Bilgisi"])
async def get_available_agents():
    """
    Sistemdeki mevcut agentların listesini döndürür
    """
    return ["rehberlik", "öneri", "motivasyon", "koc"]


@app.get("/collections", response_model=List[str], tags=["Döküman Yönetimi"])
async def get_available_collections():
    """
    Vector store'daki koleksiyonların listesini döndürür
    """
    try:
        service = await get_document_service()
        return list(service.collections.keys())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Koleksiyonlar listelenirken hata oluştu: {str(e)}")


@app.post("/collections/create", response_model=CollectionActionResponse, tags=["Döküman Yönetimi"])
async def create_collection(request: CreateCollectionRequest):
    """
    Yeni bir koleksiyon oluşturur
    """
    try:
        service = await get_document_service()
        result = await service.create_collection(request.collection_name, request.description)
        
        if not result["success"]:
            return JSONResponse(
                status_code=400,
                content=result
            )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Koleksiyon oluşturulurken hata oluştu: {str(e)}")


@app.post("/collections/delete", response_model=CollectionActionResponse, tags=["Döküman Yönetimi"])
async def delete_collection(request: DeleteCollectionRequest):
    """
    Bir koleksiyonu siler
    """
    try:
        service = await get_document_service()
        result = await service.delete_collection(request.collection_name)
        
        if not result["success"]:
            return JSONResponse(
                status_code=400,
                content=result
            )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Koleksiyon silinirken hata oluştu: {str(e)}")

@app.post("/collections/reset", response_model=CollectionActionResponse, tags=["Döküman Yönetimi"])
async def reset_collection(request: ResetCollectionRequest):
    """
    Bir koleksiyonu sıfırlar (temizler ve yeniden oluşturur)
    """
    try:
        service = await get_document_service()
        result = await service.clean_and_recreate_collection(request.collection_name)
        
        if not result["success"]:
            return JSONResponse(
                status_code=400,
                content=result
            )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Koleksiyon sıfırlanırken hata oluştu: {str(e)}")


@app.get("/collections/stats", tags=["Döküman Yönetimi"])
async def get_collection_stats():
    """
    Koleksiyonlardaki doküman sayılarını döndürür
    """
    try:
        service = await get_document_service()
        collections_info = await service.get_all_collections()
        return collections_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Koleksiyon istatistikleri alınamadı: {str(e)}")
    

@app.get("/health", tags=["Sistem Bilgisi"])
async def health_check():
    """
    API'nin çalışır durumda olup olmadığını kontrol eder
    """
    if not OPENAI_API_KEY:
        return {"status": "warning", "message": "OpenAI API anahtarı yapılandırılmamış"}
    
    # Milvus bağlantısını da kontrol et
    try:
        connections.connect(
            alias="default", 
            host=MILVUS_HOST, 
            port=MILVUS_PORT
        )
        return {"status": "ok", "message": "Sistem çalışıyor", "milvus_status": "connected"}
    except Exception as e:
        return {"status": "warning", "message": f"OpenAI API bağlantısı tamam, Milvus bağlantı hatası: {str(e)}"}

@app.get("/")
async def root():
    """
    Kök URL'den dökümantasyona yönlendir
    """
    return RedirectResponse(url="/docs")

# İşlem sonlandırıldığında geçici dosyaları temizle
@app.on_event("shutdown")
def shutdown_event():
    """
    Uygulama kapatıldığında yapılması gereken temizlik işlemleri
    """
    # Temp klasöründeki tüm dosyaları temizle
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Dosya silinemedi {file_path}: {e}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)