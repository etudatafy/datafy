#!/usr/bin/env python
# load_coaches.py
import os
import json
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

# .env dosyasını yükle
load_dotenv()

# API anahtarını al
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

def parse_float_to_int(value):
    if not value or value == "" or pd.isna(value):
        return 0
    try:
        if isinstance(value, (int, float)):
            return int(value)
        else:
            return int(float(value)) if value.strip() else 0
    except (ValueError, TypeError):
        return 0

def create_coach_collection():
    print("Milvus'a bağlanılıyor...")
    connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
    
    # Collection adı
    collection_name = "koc_collection"
    
    # Collection'ın var olup olmadığını kontrol et
    if utility.has_collection(collection_name):
        print(f"Collection '{collection_name}' zaten mevcut. Siliniyor...")
        utility.drop_collection(collection_name)
        print(f"Collection '{collection_name}' silindi.")
    
    # Collection şemasını oluştur
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),  
        FieldSchema(name="isim_soyisim", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="okul", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="bolum", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="biyografi", dtype=DataType.VARCHAR, max_length=5000),
        FieldSchema(name="kocluk_ucreti", dtype=DataType.INT64),  # Filtreleme kriterleri
        FieldSchema(name="tecrube_sene", dtype=DataType.INT64),   # Filtreleme kriterleri
        FieldSchema(name="mezuna_kaldi", dtype=DataType.BOOL),    # Filtreleme kriterleri
        FieldSchema(name="mezun_ogrenci_kabul", dtype=DataType.BOOL),  # Filtreleme kriterleri
        FieldSchema(name="alt_sinif_kabul", dtype=DataType.BOOL),      # Filtreleme kriterleri
        FieldSchema(name="kocluk_alani", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="guclu_alanlar", dtype=DataType.VARCHAR, max_length=200),
        
        # İlk sınav sonuçları - TYT ve diğer
        FieldSchema(name="tyt_derece_ilk", dtype=DataType.INT64),
        FieldSchema(name="sayisal_derece_ilk", dtype=DataType.INT64),
        FieldSchema(name="sozel_derece_ilk", dtype=DataType.INT64),
        FieldSchema(name="ea_derece_ilk", dtype=DataType.INT64), 
        FieldSchema(name="dil_derece_ilk", dtype=DataType.INT64),
        
        # Son sınav sonuçları - TYT ve diğer
        FieldSchema(name="tyt_derece_son", dtype=DataType.INT64),
        FieldSchema(name="sayisal_derece_son", dtype=DataType.INT64),
        FieldSchema(name="sozel_derece_son", dtype=DataType.INT64),
        FieldSchema(name="ea_derece_son", dtype=DataType.INT64),
    ]
    
    print("Koleksiyon şeması oluşturuluyor...")
    schema = CollectionSchema(fields, "Coach profilleri için vektör koleksiyonu")
    collection = Collection(name=collection_name, schema=schema)
    print(f"Collection '{collection_name}' oluşturuldu.")
    
    return collection

def load_coaches_data(coaches_data, collection):
    """
    Koç verilerini Milvus'a yükler
    
    Args:
        coaches_data: Koç verileri (liste olarak)
        collection: Milvus koleksiyonu
        
    Returns:
        bool: İşlemin başarılı olup olmadığı
    """
    print(f"{len(coaches_data)} koç profili işlenecek.")
    
    try:
        # OpenAI embeddings modelini başlat
        print("OpenAI embeddings modeli başlatılıyor...")
        embeddings_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        # Koç verilerini işle
        print("Koç verileri işleniyor...")
        
        embeddings = []
        isim_soyisim_list = []
        okul_list = []
        bolum_list = []
        biyografi_list = []
        kocluk_ucreti_list = []
        tecrube_sene_list = []
        mezuna_kaldi_list = []
        mezun_ogrenci_kabul_list = []
        alt_sinif_kabul_list = []
        kocluk_alani_list = []
        guclu_alanlar_list = []
        
        # İlk sınav sonuçları
        tyt_derece_ilk_list = []
        sayisal_derece_ilk_list = []
        sozel_derece_ilk_list = []
        ea_derece_ilk_list = []
        dil_derece_ilk_list = []
        
        # Son sınav sonuçları
        tyt_derece_son_list = []
        sayisal_derece_son_list = []
        sozel_derece_son_list = []
        ea_derece_son_list = []
        
        for idx, coach in enumerate(coaches_data):
            isim_soyisim = coach.get("İsim Soyisim", "")
            print(f"Koç profili işleniyor {idx+1}/{len(coaches_data)}: {isim_soyisim}")
            
            # Biyografi için embedding oluştur
            biyografi = coach.get("Biyografiniz (sitedeki biyografiyi yapıştırabilirsiniz)", "")
            
            # Biyografi değerini güvenli şekilde işle
            if pd.isna(biyografi) or biyografi == "" or biyografi == "-":
                biyografi = coach.get("Biyografiniz", "")
                if pd.isna(biyografi) or biyografi == "" or biyografi == "-":
                    biyografi = coach.get("Biyografi", "")
                    if pd.isna(biyografi) or biyografi == "" or biyografi == "-":
                        biyografi = f"{isim_soyisim} - Koçluk profili"  
            
            # Biyografiyi string'e çevir
            biyografi = str(biyografi)
            print(f"Biyografi embedding oluşturuluyor: {biyografi[:50] if len(biyografi) > 50 else biyografi}...")
            
            embedding = embeddings_model.embed_query(biyografi)
            
            # Temel bilgileri hazırla
            okul = str(coach.get("Okuduğunuz Okul", ""))
            bolum = str(coach.get("Bölümünüz", ""))
            
            # Filtreleme alanlarını hazırla (NaN ve eksik değerleri kontrol et)
            kocluk_ucreti = parse_float_to_int(coach.get("Koçluk ücretiniz", 0))
            tecrube_sene = parse_float_to_int(coach.get("Tecrübeniz (sene)", 0))
            
            # Boolean değerler için güvenli dönüşüm
            mezuna_kaldi_val = coach.get("Mezuna kaldınız mı?", "")
            mezuna_kaldi = isinstance(mezuna_kaldi_val, str) and mezuna_kaldi_val.lower() == "evet"
            
            mezun_ogrenci_kabul_val = coach.get("Mezun bir öğrenciyle çalışmak ister misin?", "")
            mezun_ogrenci_kabul = isinstance(mezun_ogrenci_kabul_val, str) and mezun_ogrenci_kabul_val.lower() == "evet"
            
            alt_sinif_kabul_val = coach.get("Sınav senesinde olmayan (11.sınıf veya altı) bir öğrenciyle çalışmak ister misin?", "")
            alt_sinif_kabul = isinstance(alt_sinif_kabul_val, str) and alt_sinif_kabul_val.lower() == "evet"
            
            kocluk_alani = str(coach.get("Koçluk vermek istediğiniz alan(lar)", ""))
            guclu_alanlar = str(coach.get("Kendini en güçlü hissetiğin 3 alan", ""))
            
            # İlk sınav sonuçları
            tyt_derece_ilk = parse_float_to_int(coach.get("TYT Dereceniz", ""))
            sayisal_derece_ilk = parse_float_to_int(coach.get("Eğer girdiyseniz sayısal dereceniz", ""))
            sozel_derece_ilk = parse_float_to_int(coach.get("Eğer girdiyseniz sözel dereceniz", ""))
            ea_derece_ilk = parse_float_to_int(coach.get("Eğer girdiyseniz eşit ağırlık dereceniz", ""))
            dil_derece_ilk = parse_float_to_int(coach.get("Eğer girdiyseniz yabancı dil dereceniz", ""))
            
            # Son sınav sonuçları
            tyt_derece_son = parse_float_to_int(coach.get("TYT dereceniz", ""))
            sayisal_derece_son = parse_float_to_int(coach.get("Eğer girdiyseniz sayısal dereceniz.1", ""))
            sozel_derece_son = parse_float_to_int(coach.get("Eğer girdiyseniz sözel dereceniz.1", ""))
            ea_derece_son = parse_float_to_int(coach.get("Eğer girdiyseniz eşit ağırlık dereceniz.1", ""))
            
            # Listeye ekle
            embeddings.append(embedding)
            isim_soyisim_list.append(isim_soyisim)
            okul_list.append(okul)
            bolum_list.append(bolum)
            biyografi_list.append(biyografi)
            kocluk_ucreti_list.append(kocluk_ucreti)
            tecrube_sene_list.append(tecrube_sene)
            mezuna_kaldi_list.append(mezuna_kaldi)
            mezun_ogrenci_kabul_list.append(mezun_ogrenci_kabul)
            alt_sinif_kabul_list.append(alt_sinif_kabul)
            kocluk_alani_list.append(kocluk_alani)
            guclu_alanlar_list.append(guclu_alanlar)
            
            # İlk sınav sonuçlarını ekle
            tyt_derece_ilk_list.append(tyt_derece_ilk)
            sayisal_derece_ilk_list.append(sayisal_derece_ilk)
            sozel_derece_ilk_list.append(sozel_derece_ilk)
            ea_derece_ilk_list.append(ea_derece_ilk)
            dil_derece_ilk_list.append(dil_derece_ilk)
            
            # Son sınav sonuçlarını ekle
            tyt_derece_son_list.append(tyt_derece_son)
            sayisal_derece_son_list.append(sayisal_derece_son)
            sozel_derece_son_list.append(sozel_derece_son)
            ea_derece_son_list.append(ea_derece_son)
        
        if len(embeddings) == 0:
            print("Hiç koç profili işlenemedi!")
            return False
        
        # Veri ekleme işlemi
        print("Veri ekleme için hazırlanıyor...")
        insert_data = [
            embeddings,
            isim_soyisim_list,
            okul_list,
            bolum_list,
            biyografi_list,
            kocluk_ucreti_list,
            tecrube_sene_list,
            mezuna_kaldi_list,
            mezun_ogrenci_kabul_list,
            alt_sinif_kabul_list,
            kocluk_alani_list,
            guclu_alanlar_list,
            tyt_derece_ilk_list,
            sayisal_derece_ilk_list,
            sozel_derece_ilk_list,
            ea_derece_ilk_list,
            dil_derece_ilk_list,
            tyt_derece_son_list,
            sayisal_derece_son_list,
            sozel_derece_son_list,
            ea_derece_son_list
        ]
        
        # Koleksiyona veri ekleme
        print("Milvus'a veri ekleniyor...")
        insert_result = collection.insert(insert_data)
        print(f"Veri başarıyla eklendi. {len(embeddings)} koç profili eklendi.")
        
        # Index oluşturma
        print("Embedding alanı için indeks oluşturuluyor...")
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        print("İndeks başarıyla oluşturuldu.")
        
        # Koleksiyonu yükle (arama için)
        print("Koleksiyon belleğe yükleniyor...")
        collection.load()
        print("Koleksiyon başarıyla yüklendi.")
        
        return True
    except Exception as e:
        print(f"Koç verisi yükleme hatası: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def load_coaches_from_excel(excel_file_path, collection):
    """
    Excel dosyasından koç verilerini okur ve Milvus'a yükler
    
    Args:
        excel_file_path: Excel dosyasının yolu
        collection: Milvus koleksiyonu
        
    Returns:
        bool: İşlemin başarılı olup olmadığı
    """
    print(f"Excel dosyası okunuyor: {excel_file_path}")
    
    try:
        # Excel dosyasını oku
        df = pd.read_excel(excel_file_path)
        
        # Veriyi liste formatına dönüştür
        coaches_data = df.replace({np.nan: None}).to_dict('records')
        
        print(f"{len(coaches_data)} koç profili okundu.")
        
        # Koç verilerini yükle
        return load_coaches_data(coaches_data, collection)
    except Exception as e:
        print(f"Excel okuma hatası: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def load_coaches_from_json(json_file_path, collection):
    """
    JSON dosyasından koç verilerini okur ve Milvus'a yükler
    
    Args:
        json_file_path: JSON dosyasının yolu
        collection: Milvus koleksiyonu
        
    Returns:
        bool: İşlemin başarılı olup olmadığı
    """
    print(f"JSON dosyası okunuyor: {json_file_path}")
    
    try:
        # JSON dosyasını oku
        with open(json_file_path, 'r', encoding='utf-8') as f:
            coaches_data = json.load(f)
        
        # Liste olduğundan emin ol
        if not isinstance(coaches_data, list):
            coaches_data = [coaches_data]
        
        print(f"{len(coaches_data)} koç profili okundu.")
        
        # Koç verilerini yükle
        return load_coaches_data(coaches_data, collection)
    except Exception as e:
        print(f"JSON okuma hatası: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def load_coaches_from_file(file_path):
    """
    Dosyadan (Excel, JSON, CSV) koç verilerini okur ve Milvus'a yükler
    
    Args:
        file_path: Dosya yolu
    """
    print(f"Dosya yükleniyor: {file_path}")
    
    # Koleksiyonu oluştur
    collection = create_coach_collection()
    
    # Dosya türüne göre yükleme yap
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        success = load_coaches_from_excel(file_path, collection)
    elif file_path.endswith('.json'):
        success = load_coaches_from_json(file_path, collection)
    elif file_path.endswith('.csv'):
        # CSV dosyasını yükle (gerekirse ileride eklenebilir)
        print("CSV dosya desteği henüz eklenmedi")
        success = False
    else:
        print(f"Desteklenmeyen dosya formatı: {file_path}")
        success = False
    
    if success:
        print("Koç verileri başarıyla yüklendi!")
    else:
        print("Koç verilerini yüklerken bir hata oluştu.")
    
    # Bağlantıyı kapat
    connections.disconnect("default")
    return success

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Koç verilerini Milvus\'a yükle')
    parser.add_argument('file_path', help='Koç verileri içeren dosya yolu (Excel, JSON, CSV)')
    
    args = parser.parse_args()
    
    load_coaches_from_file(args.file_path)