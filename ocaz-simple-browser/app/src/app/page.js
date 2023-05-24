"use client";

import { useState, useEffect, useRef } from "react";

import PreviewModal from "./components/PreviewModal";
import { Thumbnail, ThumbnailContainer } from "./components/Thumbnail";
import { Pagination, PaginationContent } from "./components/Pagination";

function Gallery({
  objects,
  selectedObjectIndex,
  selectedObjectRef,
  height,
  onClick = () => {},
}) {
  return (
    <ThumbnailContainer>
      {objects.map((object) => (
        <Thumbnail
          key={object.head10mbSha1}
          object={object}
          selected={selectedObjectIndex == object.index}
          selectedObjectRef={selectedObjectRef}
          height={height}
          onClick={() => onClick(object)}
        />
      ))}
    </ThumbnailContainer>
  );
}

function scrollIntoViewWithPadding({
  element,
  padding = 50,
  behavior = "smooth",
}) {
  const rect = element.getBoundingClientRect();
  if (rect.top < 0) {
    window.scrollBy({
      left: 0,
      top: rect.top - padding,
      behavior,
    });
  } else if (rect.bottom > window.innerHeight) {
    window.scrollBy({
      left: 0,
      top: rect.bottom - window.innerHeight + padding,
      behavior,
    });
  }
}

export default function Page() {
  const selectedObjectRef = useRef(null);
  const [context, setContext] = useState({
    perPage: 100,
    page: 1,
    objects: [],
    selectedObjectIndex: null,
    isOpen: false,
  });

  const updateContext = (context) => {
    setContext((prev) => ({ ...prev, ...context }));
  };

  useEffect(() => {
    async function fetchObjects() {
      const condition = {};
      // const condition = { image: { $exists: true } };
      // const condition = { video: { $exists: true } };
      const params = { condition: JSON.stringify(condition), limit: 1000 };
      // const params = { condition: JSON.stringify(condition) };
      const queryString = new URLSearchParams(params).toString();
      const { objects } = await fetch(`/api/objects?${queryString}`).then(
        (response) => response.json()
      );
      objects.forEach((object, i) => (object.index = i));
      updateContext({
        page: 1,
        objects,
        selectedObjectIndex: 0,
        isOpen: false,
      });
    }
    fetchObjects();
  }, []);

  useEffect(() => {
    const current = selectedObjectRef?.current;
    if (current) {
      scrollIntoViewWithPadding({ element: current });
    }
  }, [context]);

  // console.log({ context });

  const numberOfPages = Math.ceil(context.objects.length / context.perPage);
  const startIndex = context.perPage * (context.page - 1);
  const endIndex = context.perPage * context.page;

  const setSelectedObjectIndex = (index) => {
    const selectedObjectIndex =
      (context.objects.length + index) % context.objects.length;
    updateContext({
      selectedObjectIndex,
      page: Math.floor(selectedObjectIndex / context.perPage) + 1,
    });
  };
  const selectPrev = () => {
    if (context.selectedObjectIndex == null) return;
    setSelectedObjectIndex(context.selectedObjectIndex - 1);
  };
  const selectNext = () => {
    if (context.selectedObjectIndex == null) return;
    setSelectedObjectIndex(context.selectedObjectIndex + 1);
  };
  const onKeyDown = (e) => {
    if (e.code == "ArrowRight") {
      selectNext();
      e.preventDefault();
    } else if (e.code == "ArrowLeft") {
      selectPrev();
      e.preventDefault();
    } else if (e.code == "Space") {
      setContext((prev) => ({ ...prev, isOpen: !prev.isOpen }));
      e.preventDefault();
    }
  };

  return (
    <main>
      <div tabIndex="0" onKeyDown={onKeyDown}>
        <Pagination
          page={context.page}
          numberOfPages={numberOfPages}
          setPage={(page) => setContext((prev) => ({ ...prev, page }))}
        />
        <PaginationContent>
          <Gallery
            objects={context.objects.slice(startIndex, endIndex)}
            selectedObjectIndex={context.selectedObjectIndex}
            selectedObjectRef={selectedObjectRef}
            height={200}
            onClick={(object) =>
              setContext((prev) => ({
                ...prev,
                selectedObjectIndex: object.index,
                isOpen: true,
              }))
            }
          />
        </PaginationContent>
        <PreviewModal
          isOpen={context.isOpen && context.selectedObjectIndex != null}
          onRequestClose={() => updateContext({ isOpen: false })}
          onPrevious={(e) => {
            e.preventDefault();
            selectPrev();
          }}
          onNext={(e) => {
            e.preventDefault();
            selectNext();
          }}
          context={context}
        />
      </div>
    </main>
  );
}
