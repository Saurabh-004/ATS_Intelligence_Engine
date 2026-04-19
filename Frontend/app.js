// ── State ──────────────────────────────────────────────────────────────────
const state = { resume: null, jd: null };
const API = '';
let resumeMode = 'pdf'; // 'pdf' | 'text'
let jdMode = 'pdf';     // 'pdf' | 'text'

// Set pdf.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc =
  'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

// ── PDF Extraction ─────────────────────────────────────────────────────────
async function extractTextFromPDF(file) {
  const arrayBuffer = await file.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
  let fullText = '';
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    const pageText = content.items.map(item => item.str).join(' ');
    fullText += pageText + '\n';
  }
  return fullText.trim();
}

// ── File Handling ──────────────────────────────────────────────────────────
async function handleFile(type, file) {
  if (!file || file.type !== 'application/pdf') {
    setStatus(type, 'Only PDF files are supported.', true);
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    setStatus(type, 'File exceeds 10MB limit.', true);
    return;
  }

  const chipName = document.getElementById(type + 'ChipName');
  const chip = document.getElementById(type + 'Chip');
  chipName.textContent = file.name;
  chip.style.display = 'flex';

  document.getElementById(type + 'DropZone').classList.add('has-file');

  setStatus(type, '⏳ Extracting text from PDF...');
  try {
    const text = await extractTextFromPDF(file);
    if (!text || text.length < 30) {
      setStatus(type, '⚠️ Could not extract enough text. Is this a scanned PDF?', true);
      return;
    }
    state[type] = text;
    setStatus(type, `✓ Extracted ${text.length.toLocaleString()} characters from ${file.name}`);

    const previewBtn = document.getElementById(type + 'PreviewBtn');
    const previewDiv = document.getElementById(type + 'Preview');
    previewDiv.textContent = text.slice(0, 1200) + (text.length > 1200 ? '\n\n… (truncated)' : '');
    previewBtn.style.display = 'inline-block';
  } catch (err) {
    setStatus(type, '✕ Failed to read PDF: ' + err.message, true);
  }
}

function setStatus(type, msg, isError = false) {
  const el = document.getElementById(type + 'Status');
  el.textContent = msg;
  el.className = 'extract-status' + (isError ? ' error' : '');
}

function clearFile(type) {
  state[type] = null;
  document.getElementById(type + 'File').value = '';
  document.getElementById(type + 'Chip').style.display = 'none';
  document.getElementById(type + 'DropZone').classList.remove('has-file');
  document.getElementById(type + 'Status').textContent = '';
  document.getElementById(type + 'PreviewBtn').style.display = 'none';
  document.getElementById(type + 'Preview').style.display = 'none';
}

function togglePreview(type) {
  const div = document.getElementById(type + 'Preview');
  const btn = document.getElementById(type + 'PreviewBtn');
  const visible = div.style.display !== 'none';
  div.style.display = visible ? 'none' : 'block';
  btn.textContent = visible
    ? (type === 'resume' ? '👁 Preview resume text' : '👁 Preview JD text')
    : '🙈 Hide preview';
}

// ── Drop Zone Setup ────────────────────────────────────────────────────────
function setupDropZone(type) {
  const zone = document.getElementById(type + 'DropZone');
  const input = document.getElementById(type + 'File');

  zone.addEventListener('click', e => {
    if (e.target.closest('.file-chip') || e.target.classList.contains('drop-link')) return;
    input.click();
  });

  input.addEventListener('change', () => {
    if (input.files[0]) handleFile(type, input.files[0]);
  });

  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleFile(type, file);
  });
}

setupDropZone('resume');
setupDropZone('jd');

// ── Mode Toggle (shared for both resume and jd) ────────────────────────────
function switchMode(type, mode) {
  if (type === 'resume') resumeMode = mode;
  else jdMode = mode;

  const cap = type.charAt(0).toUpperCase() + type.slice(1);

  document.getElementById(type + 'PdfMode').style.display  = mode === 'pdf'  ? 'block' : 'none';
  document.getElementById(type + 'TextMode').style.display = mode === 'text' ? 'block' : 'none';
  document.getElementById(type + 'TogglePdf').classList.toggle('active',  mode === 'pdf');
  document.getElementById(type + 'ToggleText').classList.toggle('active', mode === 'text');

  if (mode === 'pdf') {
    document.getElementById(type + 'Textarea').value = '';
    updateCharCount(type);
  } else {
    clearFile(type);
  }
}

// ── Get text from whichever mode is active ─────────────────────────────────
function getText(type) {
  const mode = type === 'resume' ? resumeMode : jdMode;
  if (mode === 'text') {
    return document.getElementById(type + 'Textarea').value.trim();
  }
  return state[type];
}

// ── Character Counters ─────────────────────────────────────────────────────
function updateCharCount(type) {
  const textarea = document.getElementById(type + 'Textarea');
  const len = textarea ? textarea.value.length : 0;
  const counter = document.getElementById(type + 'CharCount');
  if (counter) counter.textContent = `${len.toLocaleString()} character${len !== 1 ? 's' : ''}`;
}

document.getElementById('resumeTextarea').addEventListener('input', () => updateCharCount('resume'));
document.getElementById('jdTextarea').addEventListener('input', () => updateCharCount('jd'));

// ── Analyze ────────────────────────────────────────────────────────────────
async function analyze() {
  const btn        = document.getElementById('analyzeBtn');
  const spinner    = document.getElementById('spinner');
  const btnLabel   = document.getElementById('btnLabel');
  const statusText = document.getElementById('statusText');
  const errorBox   = document.getElementById('errorBox');
  const results    = document.getElementById('results');

  errorBox.classList.remove('show');
  results.classList.remove('show');

  const resumeText = getText('resume');
  if (!resumeText || resumeText.length < 30) {
    showError(
      resumeMode === 'pdf'
        ? 'Please upload and process your resume PDF first.'
        : 'Please paste at least a few lines of resume text.'
    );
    return;
  }

  const jdText = getText('jd');
  if (!jdText || jdText.length < 30) {
    showError(
      jdMode === 'pdf'
        ? 'Please upload and process the job description PDF first.'
        : 'Please paste at least a few lines of job description text.'
    );
    return;
  }

  btn.disabled = true;
  spinner.classList.add('active');
  btnLabel.textContent = 'Analyzing...';
  statusText.textContent = 'Sending to backend...';

  try {
    const resumeFile = document.getElementById('resumeFile').files[0];
    const jdFile     = document.getElementById('jdFile').files[0];
    const useUpload  = (resumeMode === 'pdf' && resumeFile) || (jdMode === 'pdf' && jdFile);

    let res;
    if (useUpload) {
      // At least one PDF — send as multipart/form-data
      const form = new FormData();
      if (resumeMode === 'pdf' && resumeFile) form.append('resume_pdf', resumeFile);
      else form.append('resume_text', resumeText);
      if (jdMode === 'pdf' && jdFile) form.append('jd_pdf', jdFile);
      else form.append('job_description', jdText);
      res = await fetch(`${API}/predict/ats/upload`, { method: 'POST', body: form });
    } else {
      // Both plain text — send as JSON
      res = await fetch(`${API}/predict/ats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_text: resumeText, job_description: jdText })
      });
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    render(data);
    statusText.textContent = 'Done ✓';
  } catch (e) {
    const msg = (e.message || '').toLowerCase().includes('fetch')
      ? `Cannot reach backend at ${API}. Is your FastAPI server running?`
      : e.message;
    showError(msg);
    statusText.textContent = '';
  } finally {
    btn.disabled = false;
    spinner.classList.remove('active');
    btnLabel.textContent = 'Run Analysis';
  }
}

// ── Render Results ─────────────────────────────────────────────────────────
function render(data) {
  const s = +(data.semantic_score  || 0).toFixed(1);
  const k = +(data.keyword_score   || 0).toFixed(1);
  const f = +(data.final_ats_score || 0).toFixed(1);

  document.getElementById('finalScore').innerHTML    = `${f}<span class="score-unit">/100</span>`;
  document.getElementById('semanticScore').innerHTML = `${s}<span class="score-unit">/100</span>`;
  document.getElementById('keywordScore').innerHTML  = `${k}<span class="score-unit">/100</span>`;
  document.getElementById('feedbackBody').textContent = data.summary || 'No feedback returned.';

  document.getElementById('results').classList.add('show');

  setTimeout(() => {
    setBar('finalBar',    'finalPct',    'finalMiniBar',    f);
    setBar('semanticBar', 'semanticPct', 'semanticMiniBar', s);
    setBar('keywordBar',  'keywordPct',  'keywordMiniBar',  k);
  }, 60);
}

function setBar(barId, pctId, miniId, val) {
  const pct = Math.min(val, 100);
  document.getElementById(barId).style.width  = pct + '%';
  document.getElementById(miniId).style.width = pct + '%';
  document.getElementById(pctId).textContent  = val + '%';
}

// ── Utilities ──────────────────────────────────────────────────────────────
function showError(msg) {
  const box = document.getElementById('errorBox');
  box.textContent = msg;
  box.classList.add('show');
}

function clearAll() {
  clearFile('resume');
  clearFile('jd');
  document.getElementById('resumeTextarea').value = '';
  document.getElementById('jdTextarea').value = '';
  updateCharCount('resume');
  updateCharCount('jd');
  switchMode('resume', 'pdf');
  switchMode('jd', 'pdf');
  document.getElementById('results').classList.remove('show');
  document.getElementById('errorBox').classList.remove('show');
  document.getElementById('statusText').textContent = '';
}