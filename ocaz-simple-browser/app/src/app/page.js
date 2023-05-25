"use client";

import { useState, useEffect, useRef } from "react";
import useSWR from "swr";

import { find } from "./lib/finder";
import { Pagination, PaginationContent } from "./components/Pagination";
import { Thumbnail, ThumbnailContainer } from "./components/Thumbnail";
import PreviewModal from "./components/PreviewModal";

async function findObjects({ ...params }) {
  return find({ ...params, collection: "object" });
}

async function findObjectIds({ ...params }) {
  const response = await findObjects({
    ...params,
    projection: { _id: 1 },
    sort: [["_id", 1]],
  });
  const objectIds = response.records.map((object) => object["_id"]);
  const objectIdToIndex = {};
  const indexToObjectId = {};
  objectIds.forEach((objectId, i) => {
    objectIdToIndex[objectId] = i;
    indexToObjectId[i] = objectId;
  });
  return { objectIds, objectIdToIndex, indexToObjectId };
}

function Gallery({
  objectIds,
  selectedObjectId,
  selectedObjectRef,
  height,
  onClick = () => {},
}) {
  const { data, error } = useSWR(
    {
      condition: { _id: { $in: objectIds } },
    },
    findObjects
  );

  if (error) return <div>Error</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <ThumbnailContainer>
      {data.records.map((object) => (
        <Thumbnail
          key={object._id}
          object={object}
          selected={selectedObjectId == object._id}
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
    selectedObjectId: null,
    isOpen: false,
  });
  const { data, error } = useSWR(
    {
      condition: {},
      // condition: { mimeType: "image/jpeg" },
      limit: 1000, // DEBUG:
    },
    findObjectIds
  );

  const updateContext = (context) => {
    setContext((prev) => ({ ...prev, ...context }));
  };

  useEffect(() => {
    const current = selectedObjectRef.current;
    if (current) {
      scrollIntoViewWithPadding({ element: current });
    }
  }, [context]);

  useEffect(() => {
    if (!data) return;
    if (context.selectedObjectId) return;
    if (data.objectIds.length <= 0) return;
    updateContext({ selectedObjectId: data.objectIds[0] });
  }, [data]);

  if (error) return <div>Error</div>;
  if (!data) return <div>Loading...</div>;

  const numberOfPages = Math.ceil(data.objectIds.length / context.perPage);
  const startIndex = context.perPage * (context.page - 1);
  const endIndex = context.perPage * context.page;
  const slicedObjectIds = data.objectIds.slice(startIndex, endIndex);

  const setSelectedObjectIndex = (index) => {
    const selectedObjectIndex =
      (data.objectIds.length + index) % data.objectIds.length;
    updateContext({
      selectedObjectId: data.indexToObjectId[selectedObjectIndex],
      page: Math.floor(selectedObjectIndex / context.perPage) + 1,
    });
  };
  const selectPrev = () => {
    if (context.selectedObjectId == null) return;
    setSelectedObjectIndex(data.objectIdToIndex[context.selectedObjectId] - 1);
  };
  const selectNext = () => {
    if (context.selectedObjectId == null) return;
    setSelectedObjectIndex(data.objectIdToIndex[context.selectedObjectId] + 1);
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
            objectIds={slicedObjectIds}
            selectedObjectId={context.selectedObjectId}
            selectedObjectRef={selectedObjectRef}
            height={200}
            onClick={(object) =>
              setContext((prev) => ({
                ...prev,
                selectedObjectId: object._id,
                isOpen: true,
              }))
            }
          />
        </PaginationContent>
        <PreviewModal
          isOpen={context.isOpen && context.selectedObjectId != null}
          onRequestClose={() => updateContext({ isOpen: false })}
          onPrevious={(e) => {
            e.preventDefault();
            selectPrev();
          }}
          onNext={(e) => {
            e.preventDefault();
            selectNext();
          }}
          objectId={context.selectedObjectId}
        />
      </div>
    </main>
  );
}
