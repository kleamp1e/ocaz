import ImageThumbnail from "./ImageThumbnail";
import VideoThumbnail from "./VideoThumbnail";

export default function Thumbnail({ object, height }) {
  if ("image" in object) {
    return <ImageThumbnail object={object} height={height} />;
  } else if ("video" in object) {
    return <VideoThumbnail object={object} height={height} />;
  } else {
    return null;
  }
}
