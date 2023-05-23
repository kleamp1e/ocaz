export default function VideoThumbnail({ object, height }) {
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
          onMouseOver={(e) => e.target.play()}
          onMouseOut={(e) => e.target.pause()}
        />
        <div
          style={{
            position: "absolute",
            top: "3px",
            left: "6px",
            opacity: 0.7,
            pointerEvents: "none",
          }}
        >
          🎬
        </div>
      </div>
    </div>
  );
}
