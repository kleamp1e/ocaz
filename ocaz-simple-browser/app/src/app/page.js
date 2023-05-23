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
  const [context, setContext] = useState({
    perPage: 3,
    page: 1,
    objects: [],
    selectedObjectIndex: null,
    isOpen: false,
  });

  useEffect(() => {
    async function fetchObjects() {
      // const condition = {};
      const condition = { image: { $exists: true } };
      // const condition = { video: { $exists: true } };
      const params = { condition: JSON.stringify(condition), limit: 30 };
      const queryString = new URLSearchParams(params).toString();
      const { objects } = await fetch(`/api/objects?${queryString}`).then(
        (response) => response.json()
      );
      objects.forEach((object, i) => (object.index = i));
      setContext((prev) => ({
        ...prev,
        page: 1,
        objects,
        selectedObjectIndex: 0,
        isOpen: false,
      }));
    }
    fetchObjects();
  }, []);

  console.log({ context });

  const numberOfPages = Math.ceil(context.objects.length / context.perPage);
  const startIndex = context.perPage * (context.page - 1);
  const endIndex = context.perPage * context.page;

  return (
    <main>
      <div>
        {Array.from({ length: numberOfPages }, (_, i) => i + 1).map((page) => (
          <button
            key={page}
            onClick={() => setContext((prev) => ({ ...prev, page }))}
          >
            {page}
          </button>
        ))}
      </div>
      <Gallery
        objects={context.objects.slice(startIndex, endIndex)}
        height={200}
        onClick={(object) =>
          setContext((prev) => ({
            ...prev,
            selectedObjectIndex: object.index,
            isOpen: true,
          }))
        }
      />
      <Modal
        isOpen={context.isOpen && context.selectedObjectIndex != null}
        onRequestClose={() =>
          setContext((prev) => ({ ...prev, isOpen: false }))
        }
        style={modalStyle}
        ariaHideApp={false}
      >
        {context.isOpen && context.selectedObjectIndex != null && (
          <Preview object={context.objects[context.selectedObjectIndex]} />
        )}
      </Modal>
    </main>
  );
}
