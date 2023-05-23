import styles from "./ImageThumbnail.module.css";

export default function ImageThumbnail({ object, height }) {
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
          className={styles.image}
          src={`/api/forwarder/object/head10mbSha1/${object.head10mbSha1}`}
          loading="lazy"
        />
      </div>
    </div>
  );
}
