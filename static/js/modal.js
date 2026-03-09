/* ─────────────────────────────────────────────────────────────
   VIDEO MODAL
   File: static/js/modal.js

   Cara pakai:
   Ganti nilai YT_VIDEO_ID di bawah dengan ID video YouTube kamu.
   Contoh URL : https://www.youtube.com/watch?v=abc123XYZ
   ID-nya      : abc123XYZ
───────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', function () {

  var YT_VIDEO_ID = '59S1IIoFhDM'; /* ← GANTI DENGAN ID VIDEO YOUTUBE KAMU */

  var overlay  = document.getElementById('videoModal');
  var closeBtn = document.getElementById('videoModalClose');
  var iframe   = document.getElementById('videoModalFrame');
  var openBtn  = document.getElementById('btnVideoModal');

  /* Jika elemen tidak ditemukan, keluar */
  if (!overlay || !closeBtn || !iframe || !openBtn) return;

  /* URL embed YouTube — autoplay=1 langsung play saat modal buka */
  var embedURL = 'https://www.youtube.com/embed/' + YT_VIDEO_ID
               + '?autoplay=1&rel=0&modestbranding=1';

  /* ── Buka modal ── */
  function openModal() {
    iframe.src = embedURL;              /* set src di sini = autoplay aktif */
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden'; /* cegah scroll di belakang */
  }

  /* ── Tutup modal ── */
  function closeModal() {
    overlay.classList.remove('active');
    document.body.style.overflow = '';

    /* Kosongkan src setelah animasi fade-out (380ms) agar video benar-benar berhenti */
    window.setTimeout(function () {
      iframe.src = '';
    }, 380);
  }

  /* Event: tombol "Pelajari Lebih" */
  openBtn.addEventListener('click', openModal);

  /* Event: tombol × */
  closeBtn.addEventListener('click', closeModal);

  /* Event: klik area gelap di luar box video */
  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) closeModal();
  });

  /* Event: tekan tombol Escape */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay.classList.contains('active')) {
      closeModal();
    }
  });

});
