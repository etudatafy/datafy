YKS AI Koçluk Sistemi - Frontend

Bu proje, YKS AI Koçluk Sistemi'nin frontend kısmını içerir. React, Vite, ve React Router kullanılarak geliştirilmiştir.

🗋l Gereksinimler

Projeyi çalıştırmadan önce aşağıdaki araçların sisteminizde kurulu olduğundan emin olun:

Node.js (LTS sürümü) ("Önerilen sürüm: v18.x veya v16.x")

Git (Kodun versiyon kontrolü için)

🚀 Kurulum Adımları

Aşağıdaki adımları takip ederek projeyi kurabilir ve çalıştırabilirsiniz:

Projeyi Kopyalayın:

git clone <repository-url>
cd frontend

Bağımlılıkları Kurun:

npm install

Geliştime Sunucusunu Başlatın:

npm run dev

Projenizi Tarayıcıda Görün:

Tarayıcınızı açın ve şu adrese gidin: http://localhost:5173.

🔀 Proje Yapısı

Projede klasör yapısı şu şekilde düzenlenmiştir:

/frontend
│── /src
│ ├── /assets → Görseller ve statik dosyalar
│ ├── /components → Yeniden kullanılabilir React bileşenleri
│ ├── /context → Global Context API yapılandırmaları
│ ├── /hooks → Özel React hook'ları
│ ├── /pages → Uygulamanın sayfa bileşenleri (Home, Dashboard)
│ ├── /redux → Redux store ve slice'lar
│ ├── /styles → CSS dosyaları ve stiller
│ ├── App.jsx → Uygulamanın ana bileşen
│ ├── main.jsx → React uygulamasını DOM'a bağlar
│── package.json → Proje bağımlılıkları ve script'ler
│── README.md → Bu doküman

📚 Proje Özellikleri

1. Routing

React Router ile Home ve Dashboard gibi farklı sayfalar arasında gezinme.

2. API Yapılandırması

Axios ile backend API'lerine bağlanmak için yapılandırma (src/api.js).

3. Modüler Proje Yapısı

Kodun okunabilirliği ve sürdürülebilirliği için bileşenler, sayfalar, stiller ve diğer parçalar ayrı klasörlerde organize edilmiştir.

⚙️ Backend Bağlantısı

Backend hazır olduğunda, frontend otomatik olarak bağlanacak şekilde yapılandırılmıştır. Şu anda, http://localhost:5000 adresinde çalışan bir backend API'sini kullanacak şekilde ayarlanmıştır. Backend çalıştırılmadığında API çağrıları başarısız olur ancak frontend bu durumdan etkilenmez.

🛠️ Sorun Giderme

1. npm install Hatası

Eğer bağımlılıkları yüklerken sorun yaşarsanız:

npm cache clean --force
npm install

2. Node.js veya NPM Eksik

Node.js ve npm'in kurulu olduğundan emin olun. İndirme ve kurulum için: https://nodejs.org

3. Tarayıcıda Sayfa Açılmıyor

Terminalde çalışan npm run dev komutunun çıktısında belirtilen localhost:5173 adresini kontrol edin.

Sunucu çalışmıyorsa, terminale şu komutları tekrar çalıştırın:

npm run dev

📄 Gelecek Planları

UI İyileştirmeleri:

Daha temiz bir görünüm ve kullanıcı deneyimi için Tailwind CSS entegrasyonu.

Backend Entegrasyonu:

Gerçek API çağrılarının bağlanması ve test edilmesi.

State Yönetimi:

Redux Toolkit ile global state yönetimi.

✨ Ekip Üyeleri için Notlar

Ekip arkadaşlarınız projeyi kurmak için yukarıdaki adımları takip edebilir. Eğer bir sorun yaşanırsa, terminal çıktısını paylaşarak birlikte çözüm bulabiliriz.

Bu dokümanı her commit veya değişiklikten sonra güncelleyebilirsiniz. ☺️
