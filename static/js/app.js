let originalImageData = null;
let currentImageData = null;
let isProcessing = false;

const controls = {
    brightness: document.getElementById('brightness'),
    contrast: document.getElementById('contrast'),
    saturation: document.getElementById('saturation'),
    sharpness: document.getElementById('sharpness'),
    temperature: document.getElementById('temperature'),
    hue: document.getElementById('hue'),
    hslSaturation: document.getElementById('hslSaturation'),
    lightness: document.getElementById('lightness')
};

const valueDisplays = {
    brightness: document.getElementById('brightnessValue'),
    contrast: document.getElementById('contrastValue'),
    saturation: document.getElementById('saturationValue'),
    sharpness: document.getElementById('sharpnessValue'),
    temperature: document.getElementById('temperatureValue'),
    hue: document.getElementById('hueValue'),
    hslSaturation: document.getElementById('hslSaturationValue'),
    lightness: document.getElementById('lightnessValue')
};

const dropZone = document.getElementById('dropZone');
const imageInput = document.getElementById('imageInput');
const editorSection = document.getElementById('editorSection');
const previewImage = document.getElementById('previewImage');
const originalImage = document.getElementById('originalImage');
const loadingOverlay = document.getElementById('loadingOverlay');
const resetBtn = document.getElementById('resetBtn');
const downloadBtn = document.getElementById('downloadBtn');
const newImageBtn = document.getElementById('newImageBtn');
const cameraRadios = document.querySelectorAll('input[name="camera"]');

dropZone.addEventListener('click', () => imageInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleImageUpload(files[0]);
    }
});

imageInput.addEventListener('change', (e) => {
    const files = e.target.files;
    if (files.length > 0) {
        handleImageUpload(files[0]);
    }
});

newImageBtn.addEventListener('click', () => {
    imageInput.click();
});

async function handleImageUpload(file) {
    if (!file.type.startsWith('image/')) {
        alert('이미지 파일만 업로드 가능합니다.');
        return;
    }

    const formData = new FormData();
    formData.append('image', file);

    showLoading();

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            originalImageData = data.image;
            currentImageData = data.image;
            
            originalImage.src = data.image;
            previewImage.src = data.image;
            
            document.querySelector('.upload-section').style.display = 'none';
            editorSection.style.display = 'block';
            
            resetControls();
        } else {
            alert('이미지 업로드 실패: ' + data.error);
        }
    } catch (error) {
        alert('이미지 업로드 중 오류가 발생했습니다: ' + error.message);
    } finally {
        hideLoading();
    }
}

Object.keys(controls).forEach(key => {
    controls[key].addEventListener('input', (e) => {
        const value = e.target.value;
        if (key === 'hue') {
            valueDisplays[key].textContent = Math.round(value);
        } else if (key === 'temperature' || key === 'hslSaturation' || key === 'lightness') {
            valueDisplays[key].textContent = parseFloat(value).toFixed(2);
        } else {
            valueDisplays[key].textContent = parseFloat(value).toFixed(2);
        }
    });

    controls[key].addEventListener('change', () => {
        processImage();
    });
});

cameraRadios.forEach(radio => {
    radio.addEventListener('change', () => {
        processImage();
    });
});

let processTimeout = null;

async function processImage() {
    if (isProcessing || !originalImageData) return;

    if (processTimeout) {
        clearTimeout(processTimeout);
    }

    processTimeout = setTimeout(async () => {
        isProcessing = true;
        showLoading();

        try {
            const selectedProfile = document.querySelector('input[name="camera"]:checked').value;

            const adjustments = {
                brightness: parseFloat(controls.brightness.value),
                contrast: parseFloat(controls.contrast.value),
                saturation: parseFloat(controls.saturation.value),
                sharpness: parseFloat(controls.sharpness.value),
                temperature: parseFloat(controls.temperature.value),
                hue: parseFloat(controls.hue.value),
                hsl_saturation: parseFloat(controls.hslSaturation.value),
                lightness: parseFloat(controls.lightness.value),
                camera_profile: selectedProfile
            };

            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image: originalImageData,
                    adjustments: adjustments
                })
            });

            const data = await response.json();

            if (data.success) {
                currentImageData = data.image;
                previewImage.src = data.image;
            } else {
                alert('이미지 처리 실패: ' + data.error);
            }
        } catch (error) {
            alert('이미지 처리 중 오류가 발생했습니다: ' + error.message);
        } finally {
            isProcessing = false;
            hideLoading();
        }
    }, 300);
}

resetBtn.addEventListener('click', () => {
    resetControls();
    processImage();
});

function resetControls() {
    controls.brightness.value = 1;
    controls.contrast.value = 1;
    controls.saturation.value = 1;
    controls.sharpness.value = 1;
    controls.temperature.value = 0;
    controls.hue.value = 0;
    controls.hslSaturation.value = 0;
    controls.lightness.value = 0;

    valueDisplays.brightness.textContent = '1.0';
    valueDisplays.contrast.textContent = '1.0';
    valueDisplays.saturation.textContent = '1.0';
    valueDisplays.sharpness.textContent = '1.0';
    valueDisplays.temperature.textContent = '0';
    valueDisplays.hue.textContent = '0';
    valueDisplays.hslSaturation.textContent = '0';
    valueDisplays.lightness.textContent = '0';

    document.getElementById('profile-none').checked = true;

    if (originalImageData) {
        currentImageData = originalImageData;
        previewImage.src = originalImageData;
    }
}

downloadBtn.addEventListener('click', async () => {
    if (!currentImageData) {
        alert('다운로드할 이미지가 없습니다.');
        return;
    }

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: currentImageData
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `edited_image_${Date.now()}.jpg`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            alert('이미지 다운로드에 실패했습니다.');
        }
    } catch (error) {
        alert('이미지 다운로드 중 오류가 발생했습니다: ' + error.message);
    }
});

function showLoading() {
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}
