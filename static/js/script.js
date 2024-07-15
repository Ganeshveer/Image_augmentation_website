document.addEventListener('DOMContentLoaded', (event) => {
    const dropbox = document.getElementById('dropbox');
    const fileInput = document.getElementById('fileInput');

    dropbox.addEventListener('click', () => fileInput.click());

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropbox.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropbox.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropbox.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropbox.classList.add('highlight');
    }

    function unhighlight(e) {
        dropbox.classList.remove('highlight');
    }

    dropbox.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        updateDropboxText(files.length);
    }

    fileInput.addEventListener('change', function(e) {
        updateDropboxText(this.files.length);
    });

    function updateDropboxText(fileCount) {
        const dropboxText = dropbox.querySelector('p');
        if (fileCount > 0) {
            dropboxText.textContent = `${fileCount} file(s) selected`;
        } else {
            dropboxText.textContent = 'Drop files here or click to upload';
        }
    }
});