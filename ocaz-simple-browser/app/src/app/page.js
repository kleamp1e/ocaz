"use client";

import { useState, useEffect } from "react";

import Thumbnail from "./components/Thumbnail";
import ThumbnailContainer from "./components/ThumbnailContainer";

function Gallery({ objects, height }) {
  return (
    <ThumbnailContainer>
      {objects.map((object) => (
        <Thumbnail key={object.head10mbSha1} object={object} height={height} />
      ))}
    </ThumbnailContainer>
  );
}

export default function Page() {
  const [objects, setObjects] = useState([]);

  useEffect(() => {
    async function fetchObjects() {
      const { objects } = await (await fetch("/api/objects")).json();
      setObjects(objects);
    }
    fetchObjects();
  }, []);

  return (
    <main>
      <Gallery objects={objects} height={200} />
    </main>
  );
}
