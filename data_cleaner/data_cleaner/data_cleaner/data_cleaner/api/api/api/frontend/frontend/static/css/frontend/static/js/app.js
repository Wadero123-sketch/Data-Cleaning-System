// Data Cleaning System Frontend
const API_BASE = '/api';
let currentFile = null;
let currentFilePath = null;

// Upload Area Event Listeners
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');

uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

// File Upload Handler
async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentFile = file.name;
            currentFilePath = data.filepath;
            displayFileInfo(data);
            enableValidation();
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError(`Upload failed: ${error.message}`);
    }
}

// Display File Information
function displayFileInfo(data) {
    const fileInfo = document.getElementById('fileInfo');
    fileInfo.classList.add('show');
    fileInfo.innerHTML = `
        <div class="report-item success">
            <strong>✓ File Uploaded:</strong> ${data.filename}<br>
            <strong>Total Rows:</strong> ${data.validation.total_rows}<br>
            <strong>Total Columns:</strong> ${data.validation.total_columns}
        </div>
    `;
}

// Validation Button
document.getElementById('validateBtn').addEventListener('click', validateData);

async function validateData() {
    if (!currentFilePath) return;
    
    try {
        const response = await fetch(`${API_BASE}/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filepath: currentFilePath })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayValidationReport(data.validation_report);
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError(`Validation failed: ${error.message}`);
    }
}

// Display Validation Report
function displayValidationReport(report) {
    const validationReport = document.getElementById('validationReport');
    validationReport.classList.add('show');
    
    let html = '<div class="report-item">';
    html += `<strong>Total Rows:</strong> ${report.total_rows}<br>`;
    html += `<strong>Total Columns:</strong> ${report.total_columns}<br>`;
    html += `<strong>Memory Usage:</strong> ${report.memory_usage.toFixed(2)} MB<br>`;
    html += `<strong>Duplicate Rows:</strong> ${report.duplicate_rows}`;
    
    if (report.issues.length > 0) {
        html += '<br><strong>Issues Found:</strong><ul>';
        report.issues.forEach(issue => {
            html += `<li>${issue}</li>`;
        });
        html += '</ul>';
    }
    
    html += '</div>';
    validationReport.innerHTML = html;
    
    enableCleaning();
}

// Cleaning Options Event Listeners
document.getElementById('handleMissing').addEventListener('change', function() {
    document.getElementById('missingOptions').classList.toggle('show', this.checked);
});

document.getElementById('removeOutliers').addEventListener('change', function() {
    document.getElementById('outlierOptions').classList.toggle('show', this.checked);
});

// Enable Cleaning Button
function enableCleaning() {
    document.getElementById('cleanBtn').disabled = false;
}

// Enable Validation Button
function enableValidation() {
    document.getElementById('validateBtn').disabled = false;
}

// Clean Data Button
document.getElementById('cleanBtn').addEventListener('click', cleanData);

async function cleanData() {
    if (!currentFilePath) return;
    
    const config = {
        filepath: currentFilePath,
        remove_duplicates: document.getElementById('removeDuplicates').checked,
        handle_missing_values: document.getElementById('handleMissing').checked,
        missing_value_strategy: document.getElementById('missingStrategy').value,
        remove_outliers: document.getElementById('removeOutliers').checked,
        outlier_method: document.getElementById('outlierMethod').value
    };
    
    try {
        const cleanBtn = document.getElementById('cleanBtn');
        cleanBtn.innerHTML = '<span class="loading"></span> Cleaning...';
        cleanBtn.disabled = true;
        
        const response = await fetch(`${API_BASE}/clean`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayCleaningReport(data);
            displayDownloadLink(data.cleaned_file);
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError(`Cleaning failed: ${error.message}`);
    } finally {
        const cleanBtn = document.getElementById('cleanBtn');
        cleanBtn.innerHTML = 'Clean Data';
        cleanBtn.disabled = false;
    }
}

// Display Cleaning Report
function displayCleaningReport(data) {
    const cleaningReport = document.getElementById('cleaningReport');
    cleaningReport.classList.add('show');
    
    const report = data.report;
    let html = `
        <div class="report-item success">
            <strong>✓ Cleaning Completed Successfully!</strong><br>
            <strong>Original Rows:</strong> ${report.original_rows}<br>
            <strong>Final Rows:</strong> ${report.final_rows}<br>
            <strong>Rows Removed:</strong> ${report.rows_removed}<br>
            <strong>Original Columns:</strong> ${report.original_columns}<br>
            <strong>Final Columns:</strong> ${report.final_columns}<br>
            <strong>Columns Removed:</strong> ${report.columns_removed}
        </div>
    `;
    
    if (report.cleaning_steps.length > 0) {
        html += '<div class="report-item"><strong>Cleaning Steps:</strong><ul>';
        report.cleaning_steps.forEach(step => {
            html += `<li>${step}</li>`;
        });
        html += '</ul></div>';
    }
    
    cleaningReport.innerHTML = html;
}

// Display Download Link
function displayDownloadLink(filename) {
    const downloadSection = document.getElementById('downloadSection');
    downloadSection.classList.add('show');
    downloadSection.innerHTML = `
        <div class="report-item">
            <strong>📥 Download Cleaned Data:</strong><br>
            <a href="${API_BASE}/download/${filename}" class="download-link">Download ${filename}</a>
        </div>
    `;
}

// Show Error Messages
function showError(message) {
    alert(`Error: ${message}`);
}
