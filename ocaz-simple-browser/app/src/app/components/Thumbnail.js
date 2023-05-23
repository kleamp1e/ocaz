"use client";

import { useState } from "react";

import styles from "./Thumbnail.module.css";

function ImageThumbnail({ object, height, onClick = null }) {
  const width = Math.floor(height * (object.image.width / object.image.height));
  return (
    <div className={styles.outer}>
      <div
        className={styles.inner}
        style={{
          width: `${width}px`,
          height: `${height}px`,
        }}
      >
        <img
          src={`/api/forwarder/object/head10mbSha1/${object.head10mbSha1}`}
          loading="lazy"
          onClick={onClick}
        />
      </div>
    </div>
  );
}

function VideoThumbnail({ object, height, onClick = null }) {
  const [isVisible, setVisible] = useState(true);
  const width = Math.floor(height * (object.video.width / object.video.height));

  return (
    <div className={styles.outer}>
      <div
        className={styles.inner}
        style={{
          width: `${width}px`,
          height: `${height}px`,
        }}
      >
        <video
          src={`/api/videoDigester/object/head10mbSha1/${object.head10mbSha1}`}
          onClick={onClick}
          onMouseOver={(e) => {
            e.target.play();
            setVisible(false);
          }}
          onMouseOut={(e) => {
            e.target.pause();
            setVisible(true);
          }}
        />
        {isVisible && <div className={styles.videoIcon}>🎥</div>}
      </div>
    </div>
  );
}

export function ThumbnailContainer({ children }) {
  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        // justifyContent: "space-between",
      }}
    >
      {children}
    </div>
  );
}

export function Thumbnail({ object, height, onClick = null }) {
  if ("image" in object) {
    return <ImageThumbnail object={object} height={height} onClick={onClick} />;
  } else if ("video" in object) {
    return <VideoThumbnail object={object} height={height} onClick={onClick} />;
  } else {
    return null;
  }
}
