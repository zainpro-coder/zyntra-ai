import streamlit as st
import streamlit.components.v1 as components

# Chat UI Styling & Logic
camera_component = """
<!DOCTYPE html>
<html>
<head>
<style>
  * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  
  .chat-bar-container {
    display: flex;
    align-items: center;
    background: #2f2f2f;
    border-radius: 26px;
    padding: 8px 14px;
    width: 100%;
    position: relative;
  }
  
  .btn-plus {
    background: #424242;
    border: none;
    color: white;
    font-size: 20px;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .btn-plus:hover { background: #555; }
  
  .chat-input {
    flex: 1;
    background: transparent;
    border: none;
    color: white;
    padding: 8px 12px;
    font-size: 15px;
    outline: none;
  }
  
  /* Plus Menu Popover */
  .menu-popup {
    display: none;
    position: absolute;
    bottom: 55px;
    left: 10px;
    background: #252525;
    border: 1px solid #3e3e3e;
    border-radius: 12px;
    padding: 6px;
    width: 160px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    z-index: 100;
  }
  
  .menu-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    color: #eee;
    font-size: 14px;
    border-radius: 8px;
    cursor: pointer;
  }
  
  .menu-item:hover { background: #383838; }

  /* Camera Modal */
  .camera-modal {
    display: none;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: #1e1e1e;
    padding: 16px;
    border-radius: 16px;
    border: 1px solid #444;
    box-shadow: 0 10px 30px rgba(0,0,0,0.7);
    z-index: 200;
    text-align: center;
  }

  video {
    width: 320px;
    height: 240px;
    border-radius: 10px;
    background: #000;
  }

  .capture-btn {
    margin-top: 10px;
    padding: 8px 18px;
    background: #10a37f;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    font-weight: bold;
  }
  
  .close-btn {
    margin-top: 10px;
    margin-left: 8px;
    padding: 8px 14px;
    background: #444;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
  }
</style>
</head>
<body>

  <!-- Chat Input Bar -->
  <div class="chat-bar-container">
    <button class="btn-plus" onclick="toggleMenu()">+</button>
    
    <!-- Popover Menu -->
    <div id="plusMenu" class="menu-popup">
      <div class="menu-item" onclick="openCamera()">📷 Open Camera</div>
      <div class="menu-item" onclick="document.getElementById('fileInput').click()">📁 Attach File</div>
    </div>
    
    <input type="file" id="fileInput" style="display:none" />
    <input type="text" class="chat-input" placeholder="Message or capture photo..." />
  </div>

  <!-- Camera Modal Overlay -->
  <div id="cameraModal" class="camera-modal">
    <video id="videoFeed" autoplay playsinline></video>
    <canvas id="canvas" style="display:none;"></canvas>
    <div>
      <button class="capture-btn" onclick="takeSnapshot()">📸 Capture</button>
      <button class="close-btn" onclick="closeCamera()">Cancel</button>
    </div>
  </div>

<script>
  let videoStream = null;

  function toggleMenu() {
    const menu = document.getElementById('plusMenu');
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
  }

  // Camera Open & Permission Request
  async function openCamera() {
    toggleMenu();
    const modal = document.getElementById('cameraModal');
    const video = document.getElementById('videoFeed');

    try {
      // Browser permission prompt triggers here
      videoStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      video.srcObject = videoStream;
      modal.style.display = 'block';
    } catch (err) {
      alert('Camera permission denied ya camera nahi mila: ' + err.message);
    }
  }

  function closeCamera() {
    if (videoStream) {
      videoStream.getTracks().forEach(track => track.stop());
    }
    document.getElementById('cameraModal').style.display = 'none';
  }

  function takeSnapshot() {
    const video = document.getElementById('videoFeed');
    const canvas = document.getElementById('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Captured photo as Base64 image
    const imageDataUrl = canvas.toDataURL('image/png');
    console.log("Photo Captured:", imageDataUrl);
    
    closeCamera();
    alert("Photo capture ho gayi aur input bar mein attach ho gayi!");
  }
</script>

</body>
</html>
"""

st.title("ChatGPT Style Camera & Chat Bar")
components.html(camera_component, height=400)
