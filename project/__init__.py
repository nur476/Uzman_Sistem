from flask import Flask,request,jsonify,session,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .extensions import db



db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:440412Bb.@localhost:5432/uzman-sistemler'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app) 
    
    with app.app_context():
        from .models import DiyetSonucu, User  
        db.create_all()
   
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

   
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    def vki_hesapla(kilo, boy):
        return kilo / ((boy / 100) ** 2)

    def diyet_oner(cevaplar):
        kilo = float(cevaplar["kilo"])
        boy = float(cevaplar["boy"])
        su = float(cevaplar["su"])
        aktivite = cevaplar["aktivite"]
        alerji = cevaplar["alerji"]
        uyku = cevaplar["uyku"]
        stres = cevaplar["stres"]
        cinsiyet = cevaplar.get("cinsiyet", "Belirtilmemiş")
        yas = int(cevaplar["yas"])

        vki = vki_hesapla(kilo, boy)
        if vki < 18.5:
            kilo_durumu = "Zayıf"
        elif 18.5 <= vki < 25:
            kilo_durumu = "Sağlıklı"    
        elif 25 <= vki < 30:
            kilo_durumu = "Şişman"
        elif 30 <= vki < 40:
            kilo_durumu = "Obez"
        else:
            kilo_durumu = "Aşırı Obez (Morbid Obez)"

        
        aciklama = (
            f"📊 Vücut Kitle İndeksiniz: {vki:.1f} olarak hesaplandı. "
            f"Bu değere göre kilo durumunuz: {kilo_durumu} kategorisindedir."
        )




        temel_su_ihtiyaci = kilo * 0.03



        if cinsiyet == "Erkek":
            temel_su_ihtiyaci += 0.5
        elif cinsiyet == "Kadın":
            temel_su_ihtiyaci += 0.25
        if yas >= 55:
            temel_su_ihtiyaci -= 0.25
        if su < temel_su_ihtiyaci:
            aciklama += f"Günlük su ihtiyacınız yaklaşık {temel_su_ihtiyaci:.1f} litredir. Mevcut tüketiminiz bu miktarın altında kalmaktadır. Daha fazla su içmeniz önerilir. "
        if vki < 18.5:
            kilo_durumu = "Zayıf"
        elif 18.5 <= vki <= 24.9:
            kilo_durumu = "Sağlıklı"
        elif 25 <= vki <= 29.9:
            kilo_durumu = "Fazla kilolu"
        elif 30 <= vki <= 39.9:
            kilo_durumu = "Obez"
        else:
            kilo_durumu = "Aşırı obez (Morbid obez)"

        aciklama = f"Vücut Kitle İndeksiniz: {vki:.1f} olarak hesaplandı. Bu değer '{kilo_durumu}' kategorisindedir. "

        if aktivite == "Düşük":
            aciklama += "Fiziksel aktivite düzeyiniz düşük. Haftada en az 150 dakika orta düzeyde egzersiz önerilir. "
        elif aktivite == "Orta":
            aciklama += "Orta düzeyde fiziksel aktiviteye sahipsiniz. Egzersiz sıklığını biraz daha artırarak daha sağlıklı sonuçlar elde edebilirsiniz. "

        if uyku == "Düzensiz":
            aciklama += "Uyku düzeniniz sağlığınızı doğrudan etkiler. Günde 7-9 saat arası düzenli uyku önerilmektedir. "

        if stres == "Yüksek":
            aciklama += "Stres düzeyiniz yüksek. Kronik stres; bağışıklık sistemi, sindirim ve psikolojik sağlık üzerinde olumsuz etkilere neden olabilir. "

        if vki > 30 and aktivite == "Düşük" and uyku == "Düzensiz" and su < temel_su_ihtiyaci:
            return {
                "diyet": "Şok Diyet",
                "aciklama": aciklama + "Vücut kitle indeksinizin obez sınıfında olması, düşük fiziksel aktivite, düzensiz uyku ve yetersiz su tüketimi hızlı kilo kaybını öncelikli kılmaktadır. Bu nedenle kısa sürede etkili olan, düşük kalorili Şok Diyet önerilmektedir. Uzun vadeli kullanımı önerilmez.",
                "bilgi_linki": "https://www.pinardemirkaya.com.tr/diyetler/sok-diyet/"
            }

        if vki > 25 and aktivite in ["Orta", "Yüksek"] and alerji != "Protein":
            return {
                "diyet": "Dukan Diyeti",
                "aciklama": aciklama + "Fazla kilolu kategorisinde yer alıyorsunuz ve yeterli düzeyde fiziksel aktiviteye sahipsiniz. Bu nedenle, düşük karbonhidrat ve yüksek protein içeren Dukan Diyeti, kas kütlenizi koruyarak yağ kaybını destekleyecek şekilde önerilmektedir.",
                "bilgi_linki": "https://www.pinardemirkaya.com.tr/diyetler/dukan-diyeti/"
            }

        if vki > 30:
            if aktivite == "Düşük" and uyku == "Düzensiz":
                return {
                    "diyet": "Düşük Karbonhidrat Diyeti",
                    "aciklama": aciklama + "Obezite ile birlikte gelen düşük fiziksel aktivite ve uyku problemleri, karbonhidrat alımının azaltılmasını gerektirir. Bu nedenle Düşük Karbonhidrat Diyeti önerilmektedir.",
                    "bilgi_linki": "https://www.pinardemirkaya.com.tr/diyetler/dusuk-karbonhidrat-diyeti/"
                }
            elif stres == "Yüksek":
                return {
                    "diyet": "Akdeniz Diyeti",
                    "aciklama": aciklama + "Yüksek stres seviyeniz göz önüne alındığında, inflamasyonu azaltan ve sinir sistemini destekleyen Akdeniz Diyeti önerilmektedir.",
                    "bilgi_linki": "https://unimeal.com/tr/lp20?utm_source=google_search&utm_medium=153804868239&utm_campaign=20550460041"
                }
            elif alerji == "Gluten":
                return {
                    "diyet": "Glutensiz Diyet",
                    "aciklama": aciklama + "Gluten intoleransı belirtmişsiniz. Bu nedenle glutensiz bir diyet sağlık sorunlarını önlemek adına gereklidir.",
                    "bilgi_linki": "https://www.memorial.com.tr/saglik-rehberi/glutensiz-diyet-nedir"
                }
            else:
                return {
                    "diyet": "Ketojenik Diyet",
                    "aciklama": aciklama + "Obezite durumunuzda, düşük karbonhidrat ve yüksek yağ içeren Ketojenik Diyet vücut yağ oranını azaltmak amacıyla önerilmektedir.",
                    "bilgi_linki": "https://www.memorial.com.tr/saglik-rehberi/ketojenik-diyet-nedir-nasil-yapilir"
                }
        elif 25 < vki <= 30:
            if aktivite == "Orta":
                return {
                    "diyet": "Dengeli Diyet",
                    "aciklama": aciklama + "Fazla kilolu kategorisindesiniz ve orta düzeyde aktiviteye sahipsiniz. Bu nedenle kontrollü kalori alımı sağlayan Dengeli Diyet önerilmektedir.",
                    "bilgi_linki": "https://www.alifesaglikgrubu.com.tr/makale/diyet-listesi/3740"
                }
            elif uyku == "Düzenli":
                return {
                    "diyet": "Akdeniz Diyeti",
                    "aciklama": aciklama + "Düzenli uyku alışkanlığınız sayesinde metabolizmanız desteklenmektedir. Bu nedenle sağlıklı yağlar ve taze gıdalar içeren Akdeniz Diyeti önerilmektedir.",
                    "bilgi_linki": "https://aysetugbasengel.com/akdeniz-diyeti-nedir-diyet-listesi-ornegi/"
                }
            elif alerji == "Laktoz":
                return {
                    "diyet": "Laktozsuz Diyet",
                    "aciklama": aciklama + "Laktoz intoleransınız bulunduğundan dolayı, sindirim sisteminizi rahatlatmak adına Laktozsuz Diyet önerilmektedir.",
                    "bilgi_linki": "https://diyetisyengamzealtinay.com/2023/12/13/laktozsuz-beslenme-nedir-laktoz-intoleransi-beslenme-onerileri/"
                }
            else:
                return {
                    "diyet": "Vejetaryen Diyet",
                    "aciklama": aciklama + "Et ürünlerini sınırlamayı tercih ediyorsanız, bitkisel temelli Vejetaryen Diyet sağlıklı ve sürdürülebilir bir alternatiftir.",
                    "bilgi_linki": "https://aysetugbasengel.com/vegan-beslenme-nedir-vegan-diyeti-nasil-yapilir/"
                }
        elif 18.5 < vki <= 25:
            if aktivite == "Yüksek":
                return {
                    "diyet": "Yüksek Proteinli Diyet",
                    "aciklama": aciklama + "Sağlıklı kilo aralığında olmanız ve yüksek düzeyde fiziksel aktivite yapmanız nedeniyle, kas yapınızı koruyacak Yüksek Proteinli Diyet önerilmektedir.",
                    "bilgi_linki": "https://www.acibadem.com.tr/hayat/yuksek-protein-diyeti-nedir/"
                }
            elif uyku == "Düzensiz" and stres == "Yüksek":
                return {
                    "diyet": "Anti-inflamatuar Diyet",
                    "aciklama": aciklama + "Uyku bozukluğu ve stres belirtileriniz doğrultusunda, iltihap önleyici etkisiyle bilinen Anti-inflamatuar Diyet önerilmektedir.",
                    "bilgi_linki": "https://www-hopkinsmedicine-org.translate.goog/health/wellness-and-prevention/anti-inflammatory-diet"
                }
            elif uyku == "Düzensiz":
                return {
                    "diyet": "Dengeli Diyet",
                    "aciklama": aciklama + "Sağlıklı kilo aralığındasınız ancak uyku düzeniniz sorunlu. Genel sağlık dengenizi korumak adına temel besin ögelerini içeren Dengeli Diyet önerilmektedir.",
                    "bilgi_linki": "https://www.alifesaglikgrubu.com.tr/makale/diyet-listesi/3740"
                }
            elif stres == "Yüksek":
                return {
                    "diyet": "MIND Diyeti",
                    "aciklama": aciklama + "Yüksek stres seviyeniz nedeniyle, beyin sağlığını destekleyen ve zihinsel yorgunluğu azaltan MIND Diyeti önerilmektedir.",
                    "bilgi_linki": "https://bilimgenc.tubitak.gov.tr/makale/mind-diyeti-saglikli-bir-beyin-icin-nasil-beslenmeli"
                }
            else:
                return {
                    "diyet": "Zon Diyeti",
                    "aciklama": aciklama + "Genel sağlık durumunuz iyi. Bu dengeyi korumak adına makro besinlerin ideal oranlarda alındığı Zon Diyeti önerilmektedir.",
                    "bilgi_linki": "https://aysetugbasengel.com/zone-diyeti-nedir-kilo-verdirir-mi/"
                }
        elif vki <= 18.5:
            if stres == "Yüksek":
                return {
                    "diyet": "Yüksek Kalorili Dengeli Diyet",
                    "aciklama": aciklama + "Zayıf kilo aralığında bulunuyorsunuz ve stres seviyeniz yüksek. Bu nedenle sağlıklı şekilde kilo alımını destekleyen Yüksek Kalorili Dengeli Diyet önerilmektedir.",
                    "bilgi_linki": "https://www.nefisyemektarifleri.com/blog/kilo-alma-programi-kilo-aldiran-diyet-listesi/"
                }
            else:
                return {
                    "diyet": "Besleyici Yoğun Diyet",
                    "aciklama": aciklama + "Zayıf kategorisindesiniz. Kalori ve besin değeri açısından zengin gıdaları temel alan Besleyici Yoğun Diyet önerilmektedir.",
                    "bilgi_linki": "https://gozdesahin.com/kilo-aldirici-ornek-liste"
                }
        else:
            return {
                "diyet": "Dengeli Diyet",
                "aciklama": aciklama + "Genel sağlık durumunuzu destekleyecek, temel besin öğelerini dengeli şekilde içeren bir diyettir.",
                "bilgi_linki": "https://www.alifesaglikgrubu.com.tr/makale/diyet-listesi/3740"
            }



    @app.route("/")
    def index():
        session.clear()
        return render_template("index.html")

    @app.route("/submit", methods=["POST"])
    def submit():
        data = request.get_json()
        for key, value in data.items():
            session[key] = value
        return jsonify({"status": "ok"})

    @app.route("/result")
    def result():
        cevaplar = dict(session)
        sonuc = diyet_oner(cevaplar)

        yeni_kayit = DiyetSonucu(
            cinsiyet=cevaplar.get("cinsiyet"),
            yas=int(cevaplar.get("yas")),
            kilo=float(cevaplar.get("kilo")),
            boy=float(cevaplar.get("boy")),
            su=float(cevaplar.get("su")),
            aktivite=cevaplar.get("aktivite"),
            alerji=cevaplar.get("alerji"),
            uyku=cevaplar.get("uyku"),
            stres=cevaplar.get("stres"),
            onerilen_diyet=sonuc["diyet"],
            aciklama=sonuc["aciklama"]
        )
        db.session.add(yeni_kayit)
        db.session.commit()

        return jsonify(sonuc)


    

    return app
