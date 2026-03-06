function previewAvatar(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    document.getElementById('avatar-preview').src = e.target.result;
  };
  reader.readAsDataURL(file);
}