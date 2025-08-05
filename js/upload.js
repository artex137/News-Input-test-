document.getElementById('upload-form').addEventListener('submit', async function (e) {
  e.preventDefault();

  const fileInput = document.getElementById('file');
  const status = document.getElementById('upload-status');

  if (!fileInput.files.length) {
    status.textContent = "Please select a file.";
    return;
  }

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  status.textContent = "Uploading...";

  try {
    const response = await fetch('/api/generate_article', {
      method: 'POST',
      body: formData,
    });

    const result = await response.json();

    if (result.success) {
      status.textContent = "Article generated! Reloading...";
      window.location.reload();
    } else {
      status.textContent = "Failed to generate article.";
    }
  } catch (err) {
    console.error(err);
    status.textContent = "Error during upload.";
  }
});
