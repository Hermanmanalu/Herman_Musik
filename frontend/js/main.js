// ===== HERMAN MUSIK - MAIN JAVASCRIPT =====

// ===== HAMBURGER MENU =====
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');
hamburger.addEventListener('click', () => {
  navLinks.classList.toggle('open');
});
navLinks.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => navLinks.classList.remove('open'));
});

// ===== MODAL =====
function openModal(nama, harga) {
  const overlay = document.getElementById('modalOverlay');
  document.getElementById('modalTitle').textContent = 'Pesan: ' + nama;
  document.getElementById('modalSub').textContent =
    'Harga mulai ' + harga + '. Hubungi kami untuk cek ketersediaan dan detail penawaran terbaik.';
  const msg = encodeURIComponent('Halo Herman Musik, saya tertarik dengan ' + nama + ' (' + harga + '). Apakah masih tersedia? Terima kasih.');
  document.getElementById('modalWaBtn').href = 'https://wa.me/6281264026989?text=' + msg;
  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('active');
  document.body.style.overflow = '';
}

function closeModalOnBg(e) {
  if (e.target === document.getElementById('modalOverlay')) closeModal();
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

// ===== FORM SUBMIT → WHATSAPP =====
function submitForm() {
  const nama = document.getElementById('nama').value.trim();
  const wa = document.getElementById('wa').value.trim();
  const tanggal = document.getElementById('tanggal').value;
  const tamu = document.getElementById('tamu').value;
  const jenis = document.getElementById('jenis').value;
  const pesan = document.getElementById('pesan').value.trim();

  if (!nama || !wa) {
    alert('Mohon isi nama dan nomor WhatsApp terlebih dahulu.');
    return;
  }

  // Kirim data ke backend sebelum redirect ke WA
  submitToBackend({ nama, wa, tanggal, tamu, jenis, pesan });

  const msg = `Halo Raja Taratak! 👋

*Nama:* ${nama}
*No. WA:* ${wa}
*Tanggal Acara:* ${tanggal || 'Belum ditentukan'}
*Estimasi Tamu:* ${tamu || 'Belum ditentukan'}
*Jenis Acara:* ${jenis || 'Belum dipilih'}
*Keterangan:* ${pesan || '-'}

Mohon informasi lebih lanjut. Terima kasih! 🙏`;

  window.open('https://wa.me/6281264026989?text=' + encodeURIComponent(msg), '_blank');
  showNotif();
}

// ===== KIRIM DATA KE BACKEND API =====
async function submitToBackend(data) {
  try {
    const response = await fetch('/api/permintaan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await response.json();
    console.log('Data tersimpan:', result);
  } catch (err) {
    // Gagal simpan ke backend tidak menghalangi WA redirect
    console.warn('Gagal simpan ke server:', err);
  }
}

// ===== NOTIFIKASI =====
function showNotif() {
  const notif = document.getElementById('notif');
  notif.classList.add('show');
  setTimeout(() => notif.classList.remove('show'), 4000);
}

// ===== NAVBAR SCROLL EFFECT =====
window.addEventListener('scroll', () => {
  const nav = document.getElementById('navbar');
  if (window.scrollY > 50) {
    nav.style.boxShadow = '0 4px 24px rgba(0,0,0,0.5)';
  } else {
    nav.style.boxShadow = 'none';
  }
});

// ===== SCROLL REVEAL =====
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.produk-card, .keunggulan-item, .paket-card, .testi-card, .step, .galeri-item').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(30px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});
