document.addEventListener("DOMContentLoaded", function () {
  const chartDiv = document.getElementById("chartData");
  const kazanımlar = JSON.parse(chartDiv.dataset.kazanımlar);
  const student_scores = JSON.parse(chartDiv.dataset.ogrenci);
  const avg_scores = JSON.parse(chartDiv.dataset.ortalama);

  const ogrenciVeri = kazanımlar.map(kod => student_scores[kod] || 0);
  const ortalamaVeri = kazanımlar.map(kod => avg_scores[kod] || 0);

  // 🔢 Maksimum y değeri: en büyük veri + %10 buffer
  const maxYValue = Math.ceil(
    Math.max(...ogrenciVeri.concat(ortalamaVeri)) * 1.1
  );

  // Öğrencinin katkı grafiği
  new Chart(document.getElementById("studentChart"), {
    type: "bar",
    data: {
      labels: kazanımlar,
      datasets: [{
        label: "Öğrencinin Kazanım Puanları",
        data: ogrenciVeri,
        backgroundColor: "rgba(220, 53, 69, 0.7)"
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: maxYValue
        }
      }
    }
  });

  // Diğer öğrencilerin ortalama katkı grafiği
  new Chart(document.getElementById("avgChart"), {
    type: "bar",
    data: {
      labels: kazanımlar,
      datasets: [{
        label: "Diğer Öğrencilerin Ortalama Puanları",
        data: ortalamaVeri,
        backgroundColor: "rgba(0, 123, 255, 0.7)"
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: maxYValue
        }
      }
    }
  });
});
