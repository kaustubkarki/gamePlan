import { useState } from "react";
import axios from "axios";
import Dropzone from "react-dropzone";
import "dropzone/dist/dropzone.css"; // Import Dropzone CSS for styling
import Button from "../components/Button";
import { Element } from "react-scroll";

const VideoUploader = () => {
  const [videoFile, setVideoFile] = useState(null);
  const [outputVideo, setOutputVideo] = useState(null);

  const buttonIcon = {
    src: "/images/plan-1.png",
    alt: "button Logo",
  };

  // Handle file drop
  const handleDrop = (acceptedFiles) => {
    setVideoFile(acceptedFiles[0]); // Save the first dropped file
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!videoFile) return;

    const formData = new FormData();
    formData.append("file", videoFile);

    try {
      const uploadResponse = await axios.post(
        "http://localhost:8000/upload-video/",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setOutputVideo(uploadResponse.data.output_url);
    } catch (error) {
      console.error("Error uploading video", error);
    }
  };

  return (
    <section>
      <Element name="create">
        <div className="flex flex-col items-center p-4 space-y-4">
          <div className="w-full max-w-md">
            <Dropzone onDrop={handleDrop} accept={{ "video/*": [] }}>
              {({ getRootProps, getInputProps }) => (
                <div
                  {...getRootProps()}
                  className="border-4 border-dashed border-blue-500 p-6 rounded-md text-center cursor-pointer hover:bg-blue-50"
                >
                  <input {...getInputProps()} />
                  <p className="text-gray-600">
                    Drag & Drop a video file here, or click to select
                  </p>
                </div>
              )}
            </Dropzone>
          </div>

          <Button
            onClick={handleUpload}
            disabled={!videoFile}
            icon={buttonIcon.src}
          >
            Upload and Process
          </Button>

          {outputVideo && (
            <div className="mt-4">
              <video controls className="max-w-full">
                <source
                  src={`http://localhost:8000${outputVideo}`}
                  type="video/mp4"
                />
              </video>
            </div>
          )}
        </div>
      </Element>
    </section>
  );
};

export default VideoUploader;
