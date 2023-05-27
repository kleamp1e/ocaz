"use client";

import { useState } from "react";

import styles from "./Thumbnail.module.css";

function formatDuration(duration) {
  const hour = Math.floor(duration / (60 * 60));
  const min = Math.floor((duration - hour * 60 * 60) / 60);
  const sec = Math.floor(duration - hour * 60 * 60 - min * 60);
  let result = "";
  if (duration > 60 * 60) result += `${hour}h`;
  if (duration > 60) result += `${min}m`;
  result += `${sec}s`;
  return result;
}

function ImageThumbnail({
  object,
  selected,
  selectedObjectRef,
  height,
  onClick = null,
}) {
  const width = Math.floor(height * (object.image.width / object.image.height));
  return (
    <div
      ref={selected ? selectedObjectRef : null}
      className={selected ? styles.outerSelected : styles.outer}
    >
      <div
        className={styles.inner}
        style={{
          width: `${width}px`,
          height: `${height}px`,
        }}
      >
        <img
          src={`/api/forwarder/object/head10mbSha1/${object._id}`}
          alt={object._id}
          loading="lazy"
          onClick={onClick}
        />
      </div>
    </div>
  );
}

function VideoThumbnail({
  object,
  selected,
  selectedObjectRef,
  height,
  onClick = null,
}) {
  const [isVisible, setVisible] = useState(true);
  const width = Math.floor(height * (object.video.width / object.video.height));

  return (
    <div
      ref={selected ? selectedObjectRef : null}
      className={selected ? styles.outerSelected : styles.outer}
    >
      <div
        className={styles.inner}
        style={{
          width: `${width}px`,
          height: `${height}px`,
        }}
      >
        <video
          src={`/api/videoDigester/object/head10mbSha1/${object._id}`}
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
        <div className={styles.duration}>
          {formatDuration(object.video.duration)}
        </div>
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

export function Thumbnail({
  object,
  selected,
  selectedObjectRef,
  height,
  onClick = null,
}) {
  if ("image" in object) {
    return (
      <ImageThumbnail
        object={object}
        selected={selected}
        selectedObjectRef={selectedObjectRef}
        height={height}
        onClick={onClick}
      />
    );
  } else if ("video" in object) {
    return (
      <VideoThumbnail
        object={object}
        selected={selected}
        selectedObjectRef={selectedObjectRef}
        height={height}
        onClick={onClick}
      />
    );
  } else {
    return null;
  }
}
