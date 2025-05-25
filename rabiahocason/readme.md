# Destek Talep Yönetim Sistemi (Flask)

## Proje Hakkında

Bu proje, Flask mikro web framework kullanılarak geliştirilmiş, kullanıcıların destek talepleri oluşturabildiği, yönetebildiği ve takip edebildiği bir destek talep yönetim sistemidir. Sistem, kullanıcılar ve adminler için farklı yetkilendirme seviyeleri sunar. Kullanıcılar sadece kendi taleplerini görebilirken, adminler tüm talepleri görüntüleyip yanıtlayabilir ve durumlarını yönetebilir.

---

## Özellikler

- **Kullanıcı Yönetimi**
  - Kayıt ve giriş işlemleri
  - Şifrelerin güvenli hashlenmesi (PBKDF2-SHA256)
  - Yetkilendirme: normal kullanıcı ve admin rollerinin ayrımı
- **Talep Yönetimi**
  - Talep oluşturma (öncelik, etiketler, konu, açıklama)
  - Talep listesi ve detayları
  - Taleplere admin tarafından yanıt verme ve durum güncelleme
  - Talep durumları: Açık, Çözüldü, vb.
- **Filtreleme & Arama**
  - Öncelik ve durum bazlı filtreleme
  - Tarih aralığına göre taleplerin listelenmesi
- **Admin Paneli**
  - Tüm talepleri görüntüleme
  - Talepleri yanıtlayabilme ve durum değiştirebilme
  - JSON formatında veri yedeği alma
- **Oturum Yönetimi**
  - Kullanıcı oturumları ve erişim kontrolü (Flask-Login)
- **Veritabanı**
  - SQLite kullanımı (SQLAlchemy ORM ile)
  - Modeller: Kullanıcı ve Talep ilişkisi
- **Basit ve Kullanıcı Dostu Arayüz**
  - Bootstrap 5 tabanlı responsive tasarım

---

## Teknolojiler & Kütüphaneler

| Teknoloji / Kütüphane | Sürüm / Notlar          |
|----------------------|------------------------|
| Python               | 3.7+                   |
| Flask                | Mikro web framework     |
| Flask-Login          | Oturum ve yetkilendirme|
| Flask-SQLAlchemy     | ORM                    |
| Werkzeug             | Şifre hashleme         |
| SQLite               | Hafif ilişkisel DB     |
| Bootstrap 5          | Responsive frontend    |

---

## Kurulum & Çalıştırma

### 1. Projeyi klonlayın veya indirin

```bash
git clone <repository_url>
cd <project_folder>

