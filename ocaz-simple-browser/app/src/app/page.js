"use client";

import Modal from "react-modal";
import { useState, useEffect } from "react";

import Thumbnail from "./components/Thumbnail";
import ThumbnailContainer from "./components/ThumbnailContainer";

function Gallery({ objects, height, onClick = () => {} }) {
  return (
    <ThumbnailContainer>
      {objects.map((object) => (
        <Thumbnail
          key={object.head10mbSha1}
          object={object}
          height={height}
          onClick={() => onClick(object)}
        />
      ))}
    </ThumbnailContainer>
  );
}

const modalStyle = {
  overlay: { backgroundColor: "rgba(0, 0, 0, 0.7)" },
  content: { backgroundColor: "#000000" },
};

function ImagePreview({ object }) {
  return (
    <img src={`/api/forwarder/object/head10mbSha1/${object.head10mbSha1}`} />
  );
}

function VideoPreview({ object }) {
  return (
    <video
      src={`/api/forwarder/object/head10mbSha1/${object.head10mbSha1}`}
      controls
    />
  );
}

export default function Page() {
  const [objects, setObjects] = useState([]);
  const [selectedObject, setSelectedObject] = useState(null);

  useEffect(() => {
    async function fetchObjects() {
      const { objects } = await (await fetch("/api/objects")).json();
      setObjects(objects);
    }
    fetchObjects();
  }, []);

  console.log({ selectedObject });

  return (
    <main>
      <Gallery
        objects={objects}
        height={200}
        onClick={(object) => setSelectedObject(object)}
      />
      <Modal
        isOpen={selectedObject != null}
        onRequestClose={() => setSelectedObject(null)}
        style={modalStyle}
        ariaHideApp={false}
      >
        <div>modal</div>
        <button onClick={() => setSelectedObject(null)}>close</button>
        {selectedObject && "image" in selectedObject && (
          <ImagePreview object={selectedObject} />
        )}
        {selectedObject && "video" in selectedObject && (
          <VideoPreview object={selectedObject} />
        )}
      </Modal>
    </main>
  );
}
