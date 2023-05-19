"use client";

import { useState, useEffect } from "react";

function ImageThumbnail({ object, height }) {
  const width = Math.floor(height * (object.image.width / object.image.height));
  return (
    <div style={{ border: "2px solid #333333" }}>
      <div
        style={{
          position: "relative",
          width: `${width}px`,
          height: `${height}px`,
        }}
      >
        <img
          style={{
            position: "absolute",
            top: "0",
            bottom: "0",
            left: "0",
            right: "0",
            width: "auto",
            height: "100%",
            objectFit: "contain",
          }}
          src={`/api/forwarder/object/head10mbSha1/${object.head10mbSha1}`}
          loading="lazy"
        />
      </div>
    </div>
  );
}

function VideoThumbnail({ object, height }) {
  const width = Math.floor(height * (object.video.width / object.video.height));
  return (
    <div style={{ border: "2px solid #333333" }}>
      <div
        style={{
          position: "relative",
          width: `${width}px`,
          height: `${height}px`,
        }}
      >
        <video
          style={{
            position: "absolute",
            top: "0",
            bottom: "0",
            left: "0",
            right: "0",
            width: "100%",
            height: "auto",
            objectFit: "contain",
          }}
          src={`/api/videoDigester/object/head10mbSha1/${object.head10mbSha1}`}
          width={width}
          height={height}
          onMouseOver={(e) => e.target.play()}
          onMouseOut={(e) => e.target.pause()}
        />
      </div>
    </div>
  );
}

function Thumbnail({ object, height }) {
  if ("image" in object) {
    return <ImageThumbnail object={object} height={height} />;
  } else if ("video" in object) {
    return <VideoThumbnail object={object} height={height} />;
  } else {
    return null;
  }
}

function ThumbnailContainer({ children }) {
  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "space-between",
      }}
    >
      {children}
    </div>
  );
}

export default function Page() {
  const [objects, setObjects] = useState([]);

  useEffect(() => {
    async function fetchObjects() {
      const { objects } = await (await fetch("/api/objects")).json();
      setObjects(objects);
    }
    fetchObjects();
  }, []);

  return (
    <main>
      <ThumbnailContainer>
        {objects.map((object) => (
          <Thumbnail key={object.head10mbSha1} object={object} height={200} />
        ))}
      </ThumbnailContainer>
    </main>
  );
}
