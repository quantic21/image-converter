const API_GATEWAY_URL = "https://17vqrak0vj.execute-api.ap-northeast-1.amazonaws.com/prod/upload";
const CLOUDFRONT_URL = "https://d24tqwhqu0ov5p.cloudfront.net";

let currentFileName = '';
let processedImageUrl = '';

document.getElementById("upload-box").addEventListener("click", function () {
    document.getElementById("file-input").click();
});

document.getElementById("file-input").addEventListener("change", function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = document.getElementById("preview-image");
            img.src = e.target.result;
            img.style.display = "block";
            document.getElementById("upload-text").style.display = "none";
        };
        reader.readAsDataURL(file);
    }
});

async function uploadImage() {
    const fileInput = document.getElementById("file-input");
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select an image.");
        return;
    }

    const width = document.getElementById("width").value;
    const height = document.getElementById("height").value;
    if (isNaN(width) || isNaN(height) || width <= 0 || height <= 0) {
        alert("Please enter valid width and height values.");
        return;
    }

    document.getElementById("status").textContent = "Requesting upload URL...";

    try {
        const response = await fetch(API_GATEWAY_URL,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify
                    ({
                        fileName: file.name,
                        fileSize: file.size,
                        contentType: file.type,
                        width: width,
                        height: height
                    })
            });

        const jsonResponse = await response.json();
        if (!jsonResponse.body) {
            console.error("API response does not contain 'body':", jsonResponse);
            return;
        }

        const responseData = JSON.parse(jsonResponse.body);
        if (!responseData.presignedUrl) {
            console.error("Pre-signed URL missing from response!", responseData);
            return;
        }

        const presignedUrl = responseData.presignedUrl;

        // Upload to S3
        const uploadResponse = await fetch(presignedUrl,
            {
                method: "PUT",
                body: file,
                headers: { "Content-Type": file.type }
            });

        if (uploadResponse.ok) {
            document.getElementById("status").textContent = "Image uploaded successfully!";
            currentFileName = file.name;
            const fileExtension = currentFileName.split('.').pop();
            const newFileName = `${width}x${height}.${fileExtension}`;
            processedImageUrl = `${CLOUDFRONT_URL}/${newFileName}`;

            // Display processed image
            const processedImg = document.getElementById("processed-image");
            processedImg.src = processedImageUrl;
            document.getElementById("result-container").style.display = "block";

            // Handle image loading status
            processedImg.onerror = () => {
                document.getElementById("status").textContent = "Processed image not available yet";
                processedImg.style.display = "none";
            };
            processedImg.onload = () => {
                document.getElementById("status").textContent = "Processed image ready!";
                processedImg.style.display = "block";
            };
        } else {
            document.getElementById("status").textContent = "Upload failed.";
        }
    }
    catch (err) {
        console.error("Error:", err);
        document.getElementById("status").textContent = "Upload failed.";
    }
}

async function downloadImage() {
    if (!processedImageUrl) {
        alert("No image to download");
        return;
    }

    try {
        const response = await fetch(processedImageUrl);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `resized-${newFileName}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        document.getElementById("status").textContent = "Download started!";
    } catch (error) {
        console.error("Download failed:", error);
        document.getElementById("status").textContent = "Download failed";
    }
}