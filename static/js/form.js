document.addEventListener("DOMContentLoaded", function () {
    const steps = document.querySelectorAll(".form-step");
    const nextButtons = document.querySelectorAll("[data-next]");
    const prevButtons = document.querySelectorAll("[data-prev]");
    const wizardSteps = document.querySelectorAll(".step-wizard .step");
    let currentStep = 0;

    function showStep(stepIndex) {
        steps.forEach((step, index) => {
            step.classList.toggle("active", index === stepIndex);
        });
        wizardSteps.forEach((step, index) => {
            step.classList.toggle("active", index === stepIndex);
        });
    }

    nextButtons.forEach(button => {
        button.addEventListener("click", () => {
            if (currentStep < steps.length - 1) {
                currentStep++;
                showStep(currentStep);
            }
        });
    });

    prevButtons.forEach(button => {
        button.addEventListener("click", () => {
            if (currentStep > 0) {
                currentStep--;
                showStep(currentStep);
            }
        });
    });

    // Form Gönderimi (Hesapla Butonu)
    const calculationForm = document.getElementById("calculationForm");
    if (calculationForm) {
        calculationForm.addEventListener("submit", function (e) {
            e.preventDefault();

            // Form elementlerini güvenli bir şekilde çekiyoruz
            const yasInput = document.getElementById("yas");
            const cinsiyetInput = document.getElementById("cinsiyet");
            const bolgeInput = document.getElementById("bolge");
            const cevreInput = document.getElementById("cevre_tipi");

            const formData = {
                yas: yasInput ? parseInt(yasInput.value) || 0 : 0,
                cinsiyet: cinsiyetInput ? parseInt(cinsiyetInput.value) || 0 : 0,
                bolge: bolgeInput ? bolgeInput.value : "Bilinmiyor",
                cevre_tipi: cevreInput ? cevreInput.value : "Standart",
                
                // Risk Faktörleri (Checkbox)
                kirsal_temas: document.getElementById("kirsal_temas")?.checked ? 1 : 0,
                kemirgen_temas: document.getElementById("kemirgen_temas")?.checked ? 1 : 0,
                
                // Belirtiler (Checkbox)
                ates: document.getElementById("ates")?.checked ? 1 : 0,
                kas_agrisi: document.getElementById("kas_agrisi")?.checked ? 1 : 0,
                bulanti: document.getElementById("bulanti")?.checked ? 1 : 0,
                nefes_darligi: document.getElementById("nefes_darligi")?.checked ? 1 : 0
            };

            // Sunucuya (Flask API) veri gönderme aşaması
            fetch("/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Sonuçları ekrana yazdırma
                    document.getElementById("riskScore").innerText = "%" + data.risk_score;
                    document.getElementById("riskStatus").innerText = data.risk_status;
                    
                    // Sonuç adımına geçiş yap
                    currentStep = steps.length - 1;
                    showStep(currentStep);
                } else {
                    alert("Hata oluştu: " + data.error);
                }
            })
            .catch(error => {
                alert("Sistem hatası: " + error.message);
            });
        });
    }
});
