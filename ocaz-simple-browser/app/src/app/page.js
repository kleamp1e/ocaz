"use client";

import Modal from "react-modal";
import { useState, useEffect } from "react";

import { Thumbnail, ThumbnailContainer } from "./components/Thumbnail";
import Preview from "./components/Preview";

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

export default function Page() {
  const [objects, setObjects] = useState([]);
  const [selectedObject, setSelectedObject] = useState(null);

  useEffect(() => {
    async function fetchObjects() {
      // const condition = {};
      const condition = { image: { $exists: true } };
      // const condition = { video: { $exists: true } };
      const params = { condition: JSON.stringify(condition) };
      const queryString = new URLSearchParams(params).toString();
      const { objects } = await fetch(`/api/objects?${queryString}`).then(
        (response) => response.json()
      );
      setObjects(objects);
    }
    fetchObjects();
  }, []);

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
        {selectedObject && <Preview object={selectedObject} />}
      </Modal>
    </main>
  );
}
