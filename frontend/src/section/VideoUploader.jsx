import { useState } from "react";
import axios from "axios";
import Dropzone from "react-dropzone";
import "dropzone/dist/dropzone.css"; // Import Dropzone CSS for styling
import Button from "../components/Button";
import { Element } from "react-scroll";
import { API_URL } from "../api";
import { Copy } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const VideoUploader = () => {
  const [videoFile, setVideoFile] = useState(null);
  const [outputVideo, setOutputVideo] = useState(null);
  const [videoApi, setVideoApi] = useState(null);
  const [progress, setProgress] = useState(0);

  const buttonIcon = {
    src: "/images/plan-1.png",
    alt: "button Logo",
  };

  const videoViewIcon = {
    src: "/images/plan-2.png",
    alt: "view video logo",
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(videoApi);
    alert("Link copied to clipboard!");
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
        `${API_URL}/upload-video/`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          onUploadProgress: (event) => {
            const percentCompleted = Math.round(
              (event.loaded * 100) / event.total
            );
            setProgress(percentCompleted);
          },
        }
      );
      setOutputVideo(uploadResponse.data.video_url);
      console.log("Video uploaded:", uploadResponse.data);
      console.log("upLoad video :", outputVideo);
    } catch (error) {
      console.error("Error uploading video", error);
      alert("Failed to upload the video. Please try again.");
    } finally {
      setProgress(0);
    }
  };

  const handleStream = () => {
    {
      outputVideo && setVideoApi(`${API_URL}/output/${outputVideo}`);
    }
    console.log(videoApi);
    // setVideoApi("http://localhost:8000/output/fixed_video.mp4");
  };

  return (
    <section>
      <Element name="create">
        <div className="container">
          <div className="flex flex-col items-center px-0 py-20 space-y-4 m-10 border-8 border-double border-[#34477C] rounded-2xl max-w-fit mx-auto ">
            <div className="flex flex-col gap-4 items-center justify-center mx-[190px]">
              <div className="w-auto">
                <h1 className="mb-2 h1 text-p4 uppercase max-lg:mb-2 max-lg:h2 max-md:mb-2 max-md:text-5xl max-md:leading-12">
                  Make it happen!
                </h1>
                <p className="max-w-fit mb-6 body-1 max-md:mb-10 mx-auto">
                  ⚽Get your own video and realize its analytics.⚽
                </p>
                <div className="w-512 mx-auto">
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
              </div>

              <Button
                onClick={handleUpload}
                disabled={!videoFile}
                icon={buttonIcon.src}
              >
                Upload and Process
              </Button>

              {/* Progress Bar */}
              {progress > 0 && (
                <div className="w-[30%] text-center">
                  <p className="text-gray-600 mb-1">
                    {" "}
                    {progress === 100
                      ? "Video uploaded, wait for response..."
                      : `Uploading ${progress}%...`}
                  </p>
                  {progress !== 100 && (
                    <div className="w-full bg-gray-300 rounded-full h-4">
                      <div
                        className="bg-blue-500 h-4 rounded-full transition-all duration-200 ease-in-out"
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                  )}
                </div>
              )}

              {outputVideo && (
                <Button icon={videoViewIcon.src} onClick={handleStream}>
                  <Dialog>
                    <DialogTrigger>View Processed video</DialogTrigger>
                    <DialogContent className="shad-dialog g7">
                      <DialogHeader>
                        <DialogTitle>Football Analytics Video</DialogTitle>
                        <DialogDescription>
                          You can share this with anyone who has this link.
                        </DialogDescription>
                      </DialogHeader>
                      <video
                        name="outputVideo"
                        width={855}
                        height={655}
                        className="rounded-xl"
                        autoPlay
                        muted
                        loop
                        controls
                        onError={(e) => {
                          alert("Failed to load the video.");
                          console.log("Error e.target.error =", e.target.error);
                          console.log(videoApi);
                        }}
                      >
                        <source
                          id="video-source"
                          src={videoApi}
                          type="video/mp4"
                        />
                      </video>

                      <div className="flex items-center space-x-2">
                        <div className="grid flex-1 gap-2">
                          <Label htmlFor="link" className="sr-only">
                            Link
                          </Label>
                          <Input
                            id="link"
                            defaultValue={videoApi}
                            readOnly
                            className="g7"
                          />
                        </div>
                        <button
                          type="submit"
                          size="sm"
                          className="px-3"
                          aria-label="Copy link to clipboard"
                          onClick={handleCopyLink}
                        >
                          <span className="sr-only">Copy</span>
                          <Copy />
                        </button>
                      </div>
                      <DialogFooter className="sm:justify-start">
                        <button
                          onClick={() => {
                            if (outputVideo) {
                              const filename =
                                videoApi.split("/").pop() ||
                                "processed_test.mp4";
                              const downloadLink = `${API_URL}/download/${filename}
                          `;
                              console.log(filename);
                              console.log(downloadLink);

                              window.open(downloadLink, "_blank").focus;
                            } else {
                              alert("No video available for download.");
                            }
                          }}
                          className="px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                          DOWNLOAD
                        </button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </Button>
              )}
              {/* space */}
              <p className="text-sm text-gray-500">
                Video processing may take up to 2 minutes. Feel free to leave
                this page and come back later!
              </p>
              {/* space */}
            </div>
          </div>
        </div>
      </Element>
    </section>
  );
};

export default VideoUploader;
