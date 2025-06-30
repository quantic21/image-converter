
const API_GATEWAY_URL = "https://17vqrak0vj.execute-api.ap-northeast-1.amazonaws.com/prod/upload";
const CLOUDFRONT_URL = "https://d24tqwhqu0ov5p.cloudfront.net/processed/";
const MAX_FILE_SIZE = 10 * 1024 * 1024;

document.getElementById("upload-box").addEventListener("click", () => document.getElementById("imageInput").click());
document.getElementById("imageInput").addEventListener("change", previewImage);

function previewImage() {
    const file = document.getElementById("imageInput").files[0];
    if (!file) return;
    if (file.size > MAX_FILE_SIZE) {
        alert("File is too large. Max size is 10MB.");
        return;
    }
    const reader = new FileReader();
    
    reader.onload = function (e) {
        document.getElementById("image-preview").src = e.target.result;
        document.getElementById("image-preview").style.display = "block";
        document.getElementById("upload-text").style.display = "none";
    };
    reader.readAsDataURL(file);
}

async function uploadImage() {
    const fileInput = document.getElementById("imageInput");
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select an image.");
        return;
    }
    const format = document.getElementById("formatSelect").value;
    document.getElementById("status").textContent = "Requesting upload URL...";
    try {
        const response = await fetch(API_GATEWAY_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ fileName: file.name, fileSize: file.size, contentType: file.type, format: format })
        });
        const jsonResponse = await response.json();
        const responseData = jsonResponse.body ? JSON.parse(jsonResponse.body) : jsonResponse;
        if (!responseData.presignedUrl) throw new Error("Pre-signed URL missing");
        await fetch(responseData.presignedUrl, {
            method: "PUT",
            body: file,
            headers: { "Content-Type": file.type }
        });
        document.getElementById("status").textContent = "Image uploaded successfully! Fetching processed image...";
        setTimeout(() => fetchProcessedImage(file.name, format), 5000);
    } catch (err) {
        console.error("Error:", err);
        document.getElementById("status").textContent = "Upload failed.";
    }
}

function fetchProcessedImage(fileName, format) {
    const processedImageUrl = `${CLOUDFRONT_URL}${fileName}.${format}`;
    document.getElementById("image-preview").src = processedImageUrl;
    document.getElementById("processed-image").src = processedImageUrl;
    document.getElementById("processed-image").style.display = "block";
    document.getElementById("download-link").href = processedImageUrl;
    document.getElementById("download-link").style.display = "block";
    document.getElementById("download-box").style.display = "block";
}