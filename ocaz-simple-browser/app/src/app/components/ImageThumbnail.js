export default function ImageThumbnail({ object, height }) {
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
