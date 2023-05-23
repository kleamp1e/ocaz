"use client";

import Modal from "react-modal";
import { useState, useEffect, useRef } from "react";

import { Thumbnail, ThumbnailContainer } from "./components/Thumbnail";
import Preview from "./components/Preview";

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

const modalStyle = {
  overlay: { backgroundColor: "rgba(0, 0, 0, 0.7)" },
  content: { backgroundColor: "rgba(0, 0, 0, 0.5)" },
};

function PageLink({ isActive, page, setPage, children }) {
  const onClick = (e) => {
    e.preventDefault();
    setPage(page);
  };
  return (
    <span style={{ margin: "0em 0.1em" }}>
      {isActive ? (
        <a style={{ cursor: "pointer" }} onClick={onClick}>
          {children}
        </a>
      ) : (
        children
      )}
    </span>
  );
}

function Pagination({ page, setPage, numberOfPages }) {
  const pageSet = new Set([
    1,
    2,
    3,
    page - 2,
    page - 1,
    page,
    page + 1,
    page + 2,
    numberOfPages - 2,
    numberOfPages - 1,
    numberOfPages,
  ]);
  const pageArray = Array.from(pageSet)
    .sort((a, b) => a - b)
    .filter((p) => p >= 1)
    .filter((p) => p <= numberOfPages)
    .reduce((memo, p) => {
      if (memo.length > 0 && memo[memo.length - 1] != p - 1) {
        memo.push(null);
      }
      memo.push(p);
      return memo;
    }, []);

  return (
    <div style={{ fontSize: "26px" }}>
      <PageLink isActive={page > 1} page={page - 1} setPage={setPage}>
        {"<<<"}
      </PageLink>
      {pageArray.map((p) =>
        p == null ? (
          "..."
        ) : (
          <PageLink key={p} isActive={p != page} page={p} setPage={setPage}>
            {p}
          </PageLink>
        )
      )}
      <PageLink
        isActive={page < numberOfPages}
        page={page + 1}
        setPage={setPage}
      >
        {">>>"}
      </PageLink>{" "}
    </div>
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
        <Pagination
          page={context.page}
          numberOfPages={numberOfPages}
          setPage={(page) => setContext((prev) => ({ ...prev, page }))}
        />
        <Modal
          isOpen={context.isOpen && context.selectedObjectIndex != null}
          onRequestClose={() => updateContext({ isOpen: false })}
          style={modalStyle}
          ariaHideApp={false}
        >
          {context.isOpen && context.selectedObjectIndex != null && (
            <Preview object={context.objects[context.selectedObjectIndex]} />
          )}
        </Modal>
      </div>
    </main>
  );
}
