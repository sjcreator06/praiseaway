function openLyricsSite(title, artist) {
    const cleanTitle = title.replace(/[\(\)&!.-/á']/g, '').trim();
    const cleanArtist = artist.replace(/[\(\)&!.-/á']/g, '').trim();
    

    const dataToSend = {
        songAndArtist: `${cleanTitle} - ${cleanArtist}`,
    };

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/receive_data", true);

    xhr.setRequestHeader("Content-Type", "application/json"); // Set Content-Type header to application/json
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {                                                               
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                window.location.href = "/lyrics?lyrics=" + encodeURIComponent(response.lyrics);
            } else {
                console.error("Failed to send data to Flask! Status:", xhr.status);
            }
        }
    };
    xhr.send(JSON.stringify(dataToSend));

    document.body.innerHTML = "<style> \
    iframe { \
        width: 100vw; \
        height: 100vh; \
        border: none; \
        position: fixed; \
        top: 0; \
        left: 0; \
        z-index: 9999; \
        background: url('https://your-image-url.jpg') no-repeat center center fixed; \
        background-size: cover; \
    } \
</style> \
<iframe src='/loading'></iframe>";
}
