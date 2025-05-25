document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const preview = document.getElementById('preview');
    const previewImage = document.getElementById('preview-image');
    const generateBtn = document.getElementById('generate-btn');
    const languageSelect = document.getElementById('language-select');
    const testText = document.getElementById('test-text');
    const fontPreview = document.getElementById('font-preview');

    // Drag and drop handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#4a90e2';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#ddd';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#ddd';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                previewImage.src = URL.createObjectURL(file);
                preview.style.display = 'block';
                generateBtn.disabled = false;
            } else {
                alert(data.error || 'Upload failed');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Upload failed');
        });
    }

    generateBtn.addEventListener('click', () => {
        const formData = new FormData();
        formData.append('language', languageSelect.value);
        formData.append('text', testText.value);
        
        // Get the latest uploaded image
        const latestImage = fileInput.files[0];
        if (!latestImage) {
            alert('Please upload a handwriting sample first');
            return;
        }
        formData.append('image', latestImage);

        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';

        fetch('/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Font';
            
            if (data.success) {
                fontPreview.style.display = 'block';
                fontPreview.src = `/static/generated/${data.generated_font}`;
                
                // Apply generated font to test text
                if (data.preview_text) {
                    const previewText = document.getElementById('preview-text');
                    previewText.textContent = data.preview_text;
                    previewText.style.fontFamily = 'generated-font';
                }
            } else {
                alert(data.error || 'Generation failed');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Generation failed');
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Font';
        });
    });
});