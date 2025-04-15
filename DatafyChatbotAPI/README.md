# DestekAL Chatbot

Şu anda 4 farklı agenti içeren bir RAG yapısı mevcut bu agentler sırasıyla: rehberlik, motivasyon, kaynak vb. önerisi ve koç önerisi görevlerinden sorumlu.
Arkaplanda Milvus'un Vector DB sini kullanıyoruz anlık olarak koçluk, öneri ve rehberlik agentları DB den veri çekiyorlar diğer agentler ve motivasyon agenti için geliştirme ve collection eklemeleri yapılacak.

Kurulumu yapmak için;

1.Python 3.10 sürümüyle bir envorinment oluşturup tüm requirementler yüklenmeli(Requirementlerı yüklemek için: python -r requirements.txt)
2.Docker Desktop uyguluması bilgisayarda mevcut olmalı.
3.Konsola "uvicorn main:app --reload" komutu yazılarak API aktifleştirilmeli.
4.Koç agenti için DB nin hazırlanması için "python load_coaches.py {pdf_path}" komutu girilmeli.
5.Yeni bir konsola streamlit run app.py yazılmalıdır.

Not: .env dosyasını oluşturup içerisine "OPENAI_API_KEY=..." şeklinde API key değerini atamalısınız.

Bu süreçlerin hepsi başarılı bir şekilde tamamlanırsa tarayıcınızda açılan sekmeden chatbota arayüzüne erişmiş olacaksınız.
