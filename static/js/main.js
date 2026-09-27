/**
 * PocketSmart AI — Main Client Interactions
 * Mobile Menu, Quantity Steppers, Upload Previews, Loading State Modals
 */

document.addEventListener('DOMContentLoaded', () => {
  // Mobile Nav Toggle
  const mobileToggle = document.getElementById('mobileNavToggle');
  const mobileDrawer = document.getElementById('mobileNavDrawer');
  if (mobileToggle && mobileDrawer) {
    mobileToggle.addEventListener('click', () => {
      mobileDrawer.classList.toggle('open');
      const expanded = mobileDrawer.classList.contains('open');
      mobileToggle.setAttribute('aria-expanded', expanded);
    });
  }

  // Quantity Stepper Controls
  initQuantitySteppers();

  // Outfit Image Upload Dropzone & Live Preview
  initImageUpload();

  // Planner Form Submissions with Sequential Loading Steps
  initPlannerFormSubmissions();
});

function initQuantitySteppers() {
  document.querySelectorAll('.quantity-stepper').forEach(stepper => {
    const input = stepper.querySelector('.qty-input');
    const minusBtn = stepper.querySelector('.qty-minus');
    const plusBtn = stepper.querySelector('.qty-plus');

    if (!input || !minusBtn || !plusBtn) return;

    minusBtn.addEventListener('click', () => {
      let val = parseInt(input.value, 10) || 0;
      const min = parseInt(input.getAttribute('min'), 10) || 0;
      if (val > min) {
        input.value = val - 1;
        input.dispatchEvent(new Event('change'));
      }
    });

    plusBtn.addEventListener('click', () => {
      let val = parseInt(input.value, 10) || 0;
      const max = parseInt(input.getAttribute('max'), 10) || 20;
      if (val < max) {
        input.value = val + 1;
        input.dispatchEvent(new Event('change'));
      }
    });
  });
}

function initImageUpload() {
  const dropzone = document.getElementById('outfitDropzone');
  const fileInput = document.getElementById('outfitImageInput');
  const previewBox = document.getElementById('imagePreviewBox');
  const previewImg = document.getElementById('imagePreviewImg');
  const fileDetails = document.getElementById('fileDetails');

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', () => fileInput.click());

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length > 0) {
      fileInput.files = dt.files;
      handleFileSelected(dt.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files[0]) {
      handleFileSelected(fileInput.files[0]);
    }
  });

  function handleFileSelected(file) {
    if (!file.type.match('image.*')) {
      alert('Please select an image file (PNG, JPG, JPEG, WEBP).');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      alert('Image file size exceeds 5MB limit.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      if (previewImg && previewBox) {
        previewImg.src = e.target.result;
        previewBox.style.display = 'block';
      }
      if (fileDetails) {
        const sizeKb = (file.size / 1024).toFixed(1);
        fileDetails.textContent = `${file.name} (${sizeKb} KB)`;
      }
    };
    reader.readAsDataURL(file);
  }
}

function initPlannerFormSubmissions() {
  const forms = document.querySelectorAll('.planner-submit-form');
  const loadingOverlay = document.getElementById('loadingOverlay');
  const step1 = document.getElementById('loadStep1');
  const step2 = document.getElementById('loadStep2');
  const step3 = document.getElementById('loadStep3');

  forms.forEach(form => {
    form.addEventListener('submit', (e) => {
      if (!loadingOverlay) return;

      // Show professional loading overlay
      loadingOverlay.classList.add('active');

      // Sequential progression simulation
      if (step1 && step2 && step3) {
        step1.classList.add('active');

        setTimeout(() => {
          step1.classList.remove('active');
          step1.classList.add('done');
          step1.querySelector('.step-bullet').innerHTML = '✓';
          step2.classList.add('active');
        }, 500);

        setTimeout(() => {
          step2.classList.remove('active');
          step2.classList.add('done');
          step2.querySelector('.step-bullet').innerHTML = '✓';
          step3.classList.add('active');
        }, 1100);
      }
    });
  });
}

let currentProductUrl = '#';

// Modal helper for product quick details
function showProductModal(title, price, platform, category, reason, image, url) {
  const modal = document.getElementById('productModal');
  if (!modal) return;
  document.getElementById('modalProductTitle').textContent = title;
  document.getElementById('modalProductPrice').textContent = price;
  document.getElementById('modalProductPlatform').textContent = platform;
  document.getElementById('modalProductCategory').textContent = category;
  document.getElementById('modalProductReason').textContent = reason;
  document.getElementById('modalProductImage').src = image;
  currentProductUrl = url || '#';
  modal.classList.add('active');
}

function visitRetailerFromModal() {
  if (currentProductUrl && currentProductUrl !== '#') {
    window.open(currentProductUrl, '_blank', 'noopener,noreferrer');
  } else {
    alert('Redirecting to verified retailer listing...');
  }
  closeProductModal();
}

function closeProductModal() {
  const modal = document.getElementById('productModal');
  if (modal) modal.classList.remove('active');
}
