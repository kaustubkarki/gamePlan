# GamePlan - Football Video Analysis System ⚽📊

**GamePlan** is an advanced **football video analysis system** that detects and tracks players, referees, and the ball using **ByteTrack and Optical Flow**. It assigns teams using **SigLip, UMAP, and KMeans clustering**, estimates **camera movement**, and calculates **speed and distance** using **Perspective Transformation**.

---

## 🚀 Features
✅ **Object Detection** - Detects players, referees, and the ball using YOLOv8  
✅ **Tracking** - Uses **ByteTrack & Optical Flow** for real-time player tracking  
✅ **Team Assignment** - Assigns players to teams using **SigLip + UMAP + KMeans**  
✅ **Camera Movement Estimation** - Detects camera shifts using **Optical Flow**  
✅ **Speed & Distance Calculation** - Uses **Perspective Transformation** for precise measurements  

---

## 🛠 Tech Stack
| Component             | Technology Used |
|-----------------------|----------------|
| **Programming Language** | Python 3.9 |
| **Object Detection** | YOLOv8 (Ultralytics) |
| **Tracking Algorithm** | ByteTrack & Optical Flow |
| **Team Clustering** | SigLip + UMAP + KMeans |
| **Camera Movement Estimation** | Optical Flow |
| **Speed & Distance Measurement** | Perspective Transformation |
| **Video Processing** | OpenCV |
| **Deep Learning** | PyTorch & Transformers |

---

## 📦 Installation Guide

### **🔹 Clone the Repository**
```bash
git clone https://github.com/yourusername/GamePlan.git
cd GamePlan
pip install -r requirements.txt
contents of input_vidos,output_videos, stubs are here https://drive.google.com/drive/folders/1WiMJU708sBWjR46_hyWrDgs8wuS8y5Mw?usp=sharing, https://drive.google.com/drive/folders/1i_0kD2QtiPIJsuItpMo71FumwtYIpKps?usp=sharing, https://drive.google.com/drive/folders/1jJio0nMdRcY8k3vwd8BSwBz0qs8OEgf_?usp=sharing
models: train using dataset of roboflow