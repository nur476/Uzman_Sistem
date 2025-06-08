##FitLife Diyet Öneri Sistemi

Bu proje, Flask tabanlı bir uzman sistemdir. Kullanıcının sağlık ve yaşam tarzı verilerine göre uygun diyet türünü önerir.

Özellikler
Kullanıcıdan yaş, cinsiyet, kilo, boy, su tüketimi, aktivite düzeyi, stres durumu gibi bilgiler alınır.
Bu bilgiler if-then (eğer-o zaman) mantığıyla oluşturulmuş kurallarla değerlendirilir.
Karar ağacı yaklaşımı kullanılarak uygun diyet tipi belirlenir.
Önerilen diyet, sistemde kayıt altına alınır.
PostgreSQL veritabanı ile çalışır.
Örnek Karar Mantığı

if vki > 30 and su < ihtiyaç and uyku == "Düzensiz":
    diyet = "Şok Diyet"
elif alerji == "Gluten":
    diyet = "Glutensiz Diyet"

    
Bu yapı karar ağacı gibi dallanarak ilerler ve en uygun sonucu verir.


