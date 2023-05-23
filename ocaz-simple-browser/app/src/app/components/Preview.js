import styles from "./Preview.module.css";

function ImagePreview({ object }) {
  return (
    <div className={styles.container}>
      <img src={`/api/forwarder/object/head10mbSha1/${object.head10mbSha1}`} />
    </div>
  );
}

function VideoPreview({ object }) {
  return (
    <div className={styles.container}>
      <video
        src={`/api/forwarder/object/head10mbSha1/${object.head10mbSha1}`}
        controls
      />
    </div>
  );
}

export default function Preview({ object }) {
  if ("image" in object) {
    return <ImagePreview object={object} />;
  } else if ("video" in object) {
    return <VideoPreview object={object} />;
  } else {
    return null;
  }
}
