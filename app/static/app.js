const tabs = document.querySelectorAll('[data-tab]');
const panels = document.querySelectorAll('[data-panel]');
const preview = document.querySelector('[data-preview]');
const previewStatus = document.querySelector('[data-preview-status]');
const carrierInput = document.querySelector('#carrier');
const protectedInput = document.querySelector('#protected');
const carrierLabel = document.querySelector('[data-carrier-label]');
const output = document.querySelector('[data-output]');
let sampleFile;
let lastProtectedFile;

const switchTab = (name) => {
  tabs.forEach((tab) => tab.classList.toggle('active', tab.dataset.tab === name));
  panels.forEach((panel) => panel.classList.toggle('hidden', panel.dataset.panel !== name));
};
tabs.forEach((tab) => tab.addEventListener('click', () => switchTab(tab.dataset.tab)));

const showPreview = (file) => {
  if (!file) return;
  preview.src = URL.createObjectURL(file);
  previewStatus.textContent = 'Carrier loaded';
};

async function loadSample() {
  try {
    const response = await fetch('/api/sample-carrier');
    const blob = await response.blob();
    sampleFile = new File([blob], 'wavevault-sample.png', { type: 'image/png' });
    showPreview(sampleFile);
    carrierLabel.textContent = 'Sample landscape ready';
  } catch {
    previewStatus.textContent = 'Sample unavailable';
  }
}
loadSample();

carrierInput.addEventListener('change', () => {
  const file = carrierInput.files[0];
  if (file) { showPreview(file); carrierLabel.textContent = file.name; }
});
protectedInput.addEventListener('change', () => { if (protectedInput.files[0]) showPreview(protectedInput.files[0]); });

document.querySelector('[data-encode-form]').addEventListener('submit', async (event) => {
  event.preventDefault();
  const error = document.querySelector('[data-encode-error]');
  error.textContent = '';
  const formData = new FormData(event.currentTarget);
  if (!carrierInput.files[0] && sampleFile) formData.set('image', sampleFile);
  output.innerHTML = '<span>…</span><div><strong>Encrypting and embedding</strong><p>Generating a lossless PNG carrier.</p></div>';
  try {
    const response = await fetch('/api/encode', { method: 'POST', body: formData });
    if (!response.ok) { const data = await response.json(); throw new Error(data.detail || 'Encoding failed.'); }
    const blob = await response.blob();
    lastProtectedFile = new File([blob], 'wavevault-protected.png', { type: 'image/png' });
    showPreview(lastProtectedFile);
    const url = URL.createObjectURL(blob);
    output.innerHTML = `<span>W</span><div><strong>Protected PNG ready</strong><p>${response.headers.get('X-WaveVault-Payload') || '?'} encrypted bytes · <a href="${url}" download="wavevault-protected.png">Download output</a></p></div>`;
  } catch (cause) {
    error.textContent = cause instanceof Error ? cause.message : 'Encoding failed.';
    output.innerHTML = '<span>!</span><div><strong>Encoding stopped</strong><p>Review the carrier, password, and message.</p></div>';
  }
});

document.querySelector('[data-decode-form]').addEventListener('submit', async (event) => {
  event.preventDefault();
  const error = document.querySelector('[data-decode-error]');
  error.textContent = '';
  const formData = new FormData(event.currentTarget);
  if (!protectedInput.files[0] && lastProtectedFile) formData.set('image', lastProtectedFile);
  if (!formData.get('image') || formData.get('image').size === 0) { error.textContent = 'Choose a protected PNG or encode one in this session.'; return; }
  try {
    const response = await fetch('/api/decode', { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Decoding failed.');
    output.innerHTML = `<span>✓</span><div><strong>Message verified and recovered</strong><p>${String(data.message).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}</p></div>`;
  } catch (cause) {
    error.textContent = cause instanceof Error ? cause.message : 'Decoding failed.';
  }
});
