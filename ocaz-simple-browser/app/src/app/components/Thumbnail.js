import ImageThumbnail from "./ImageThumbnail";
import VideoThumbnail from "./VideoThumbnail";

export default function Thumbnail({ object, height, onClick = null }) {
  if ("image" in object) {
    return <ImageThumbnail object={object} height={height} onClick={onClick} />;
  } else if ("video" in object) {
    return <VideoThumbnail object={object} height={height} onClick={onClick} />;
  } else {
    return null;
  }
}
