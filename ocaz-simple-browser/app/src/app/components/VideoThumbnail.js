"use client";

import styles from "./VideoThumbnail.module.css";
import { useState } from "react";

export default function VideoThumbnail({ object, height, onClick = null }) {
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
          className={styles.video}
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
        {isVisible && <div className={styles.videoIcon}>🎬</div>}
      </div>
    </div>
  );
}
