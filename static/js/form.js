document.addEventListener('DOMContentLoaded', function () {
    let currentStep = 1;
    const totalSteps = 4;

    const btnNext = document.getElementById('btn-next');
    const btnBack = document.getElementById('btn-back');
    const navButtons = document.getElementById('nav-buttons');

    // Adım değiştirme fonksiyonu (Sayfa yenilenmeden geçiş yapar)
    function showStep(step) {
        // Tüm adımları ve tabları gizle/aktifliğini kaldır
        document.querySelectorAll('.form-step').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.step').forEach(el => el.classList.remove('active'));

        // Hedef adımı ve tabı göster
        document.getElementById(`step-${step}`).classList.add('active');
        
        // Tabların hangisinde olduğunu görsel olarak güncelle (Sonuç adımı dahil ilk 3 tabı yakalar)
        for(let i = 1; i <= Math.min(step, 3); i++) {
            document.getElementById(`tab-${i}`).classList.add('active');
        }

        // Butonların durumunu ayarla
        if (step === 1) {
            btnBack.disabled = true;
        } else {
            btnBack.disabled = false;
        }

        if (step === 3) {
            btnNext.innerHTML = `HESAPLA <i class="fa-solid fa-wand-magic-sparkles"></i>`;
        } else if (step === totalSteps) {
            // Sonuç ekranında alt gezinti butonlarını tamamen gizle
            navButtons.style.display = 'none';
        } else {
            btnNext.innerHTML = `İLERİ <i class="fa-solid fa-chevron-right"></i>`;
        }
    }

    // İLERİ / HESAPLA Buton Tetikleyicisi
    btnNext.addEventListener('click', function () {
        if (currentStep < 3) {
            currentStep++;
            showStep(currentStep);
        } else if (currentStep === 3) {
            // Form bitti, verileri topla ve backend'e gönder
            calculateRisk();
        }
    });

    // GERİ Buton Tetikleyicisi
    btnBack.addEventListener('click', function () {
        if (currentStep > 1) {
            currentStep--;
            showStep(currentStep);
        }
    });

    // Flask Backend API'sine verileri POST eden fonksiyon
    function calculateRisk() {
        // Form verilerini obje haline getiriyoruz
        const formData = {
            yas: document.getElementById('yas').value || 30,
            cevre_tipi: document.getElementById('cevre_tipi').value,
            
            // Maruziyetler (Checkbx True/False değerini 1 veya 0'a çeviriyoruz)
            kemirgen_temasi: document.getElementById('kemirgen_temasi').checked ? 1 : 0,
            acik_alan: document.getElementById('acik_alan').checked ? 1 : 0,
            toz_maruziyeti: document.getElementById('toz_maruziyeti').checked ? 1 : 0,
            son_seyahat: document.getElementById('son_seyahat').checked ? 1 : 0,
            bagisiklik: document.getElementById('bagisiklik').checked ? 1 : 0,
            
            // Belirtiler
            ates: document.getElementById('ates').checked ? 1 : 0,
            bas_agrisi: document.getElementById('bas_agrisi').checked ? 1 : 0,
            yorgunluk: document.getElementById('yorgunluk').checked ? 1 : 0,
            kas_agrisi: document.getElementById('kas_agrisi').checked ? 1 : 0,
            bulanti: document.getElementById('bulanti').checked ? 1 : 0,
            nefes_guclugu: document.getElementById('nefes_guclugu').checked ? 1 : 0
        };

        // Arka planda `app.py` içindeki `/predict` rotasına istek atıyoruz
        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Adımı Sonuç ekranına (4) geçir
                currentStep = 4;
                showStep(currentStep);

                // Sonuçları ekrana bas
                const adSoyad = document.getElementById('ad_soyad').value || "İsimsiz Kullanıcı";
                const cevreMetni = formData.cevre_tipi == 0 ? "Kırsal Bölge" : "Kentsel Bölge";
                
                document.getElementById('res-isim').innerText = `${adSoyad} — ${cevreMetni}`;
                document.getElementById('res-skor').innerText = data.risk_skoru;
                
                const badge = document.getElementById('res-seviye');
                badge.innerText = `RİSK SEVİYESİ: ${data.risk_seviyesi}`;

                // Risk seviyesine göre renk aksanı verelim (Bordo / Turuncu / Yeşil)
                if (data.risk_seviyesi === "YÜKSEK") {
                    badge.style.backgroundColor = 'rgba(239, 68, 68, 0.2)';
                    badge.style.color = '#ef4444';
                    badge.style.borderColor = '#ef4444';
                } else if (data.risk_seviyesi === "ORTA") {
                    badge.style.backgroundColor = 'rgba(245, 158, 11, 0.2)';
                    badge.style.color = '#f59e0b';
                    badge.style.borderColor = '#f59e0b';
                } else {
                    badge.style.backgroundColor = 'rgba(16, 185, 129, 0.2)';
                    badge.style.color = '#10b981';
                    badge.style.borderColor = '#10b981';
                }

                // Dinamik tıbbi öneriler listesi oluştur
                generateSuggestions(data.risk_seviyesi, formData);
            } else {
                alert("Hata oluştu: " + data.message);
            }
        })
        .catch(err => {
            console.error(err);
            alert("Sunucuyla iletişim kurulurken bir hata oluştu.");
        });
    }

    // Risk seviyesine ve seçilen semptomlara göre dinamik öneri basan fonksiyon
    function generateSuggestions(seviye, inputs) {
        const list = document.getElementById('suggestions-list');
        list.innerHTML = ""; // Eski listeyi temizle
        
        let suggestions = [];

        if (seviye === "YÜKSEK") {
            suggestions.push("Acil olarak en yakın sağlık kuruluşuna başvurun ve kemirgen maruziyeti şüphenizi bildirin.");
            suggestions.push("Kendinizi izole edin ve başkalarıyla yakın temasınızı minimize edin.");
        } else if (seviye === "ORTA") {
            suggestions.push("Belirtilerinizi (özellikle ateş ve nefes darlığı) sonraki 48 saat boyunca yakından izleyin.");
            suggestions.push("Durumunuz kötüleşirse vakit kaybetmeden bir hekime görünün.");
        } else {
            suggestions.push("Mevcut veriler doğrultusunda acil bir risk görünmüyor; ancak genel hijyen kurallarına uymaya devam edin.");
        }

        if (inputs.toz_maruziyeti === 1 || inputs.kemirgen_temasi === 1) {
            suggestions.push("Kapalı ve riskli alanları temizlerken mutlaka N95 maske ve eldiven kullanın, ortamı havalandırın.");
        }
        
        if (inputs.nefes_guclugu === 1) {
            suggestions.push("Solunum güçlüğü akut bir durumdur; oksijen seviyenizin kontrol edilmesi için sağlık desteği alın.");
        }

        // Önerileri HTML olarak ekle
        suggestions.forEach(text => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="fa-solid fa-chevron-right"></i> ${text}`;
            list.appendChild(li);
        });
    }
});
