document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('downloadForm');
    const status = document.getElementById('status');
    const progressBarContainer = document.getElementById('progressBarContainer');
    const progressBar = document.getElementById('progressBar');
    const downloadLink = document.getElementById('downloadLink');

    progressBarContainer.style.display = 'none';
    downloadLink.style.display = 'none';

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        status.textContent = '';
        progressBar.value = 0;
        progressBarContainer.style.display = 'block';
        downloadLink.style.display = 'none';

        const formData = new FormData(form);
        fetch('/start_download', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            const downloadId = data.download_id;
            checkProgress(downloadId);
        })
        .catch(error => {
            status.textContent = 'Error starting download.';
            progressBarContainer.style.display = 'none';
        });
    });

    function checkProgress(downloadId) {
        fetch(`/progress/${downloadId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'downloading') {
                    progressBar.value = data.progress;
                    status.textContent = `Downloading... ${data.progress.toFixed(2)}%`;
                    setTimeout(() => checkProgress(downloadId), 1000);
                } else if (data.status === 'finished') {
                    progressBar.value = 100;
                    status.textContent = 'Download complete!';
                    fetchDownloadLink(downloadId);
                } else {
                    status.textContent = 'Waiting for download to start...';
                    setTimeout(() => checkProgress(downloadId), 1000);
                }
            })
            .catch(() => {
                status.textContent = 'Error checking progress.';
                progressBarContainer.style.display = 'none';
            });
    }

function fetchDownloadLink(downloadId) {
    fetch(`/progress/${downloadId}`)
        .then(response => response.json())
        .then(data => {
            if (data.title) {
                downloadLink.textContent = `Download complete: ${data.title}`;
            } else {
                downloadLink.textContent = 'Your download is ready. Please check the downloads folder.';
            }
            downloadLink.style.display = 'block';
        })
        .catch(() => {
            downloadLink.textContent = 'Your download is ready. Please check the downloads folder.';
            downloadLink.style.display = 'block';
        });
}
});
