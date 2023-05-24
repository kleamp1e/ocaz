import Modal from "react-modal";

import Preview from "./Preview";

const modalStyle = {
  overlay: { backgroundColor: "rgba(0, 0, 0, 0.7)" },
  content: { backgroundColor: "rgba(0, 0, 0, 0.5)" },
};

export default function PreviewModal({
  isOpen,
  onRequestClose,
  onPrevious,
  onNext,
  context,
}) {
  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      style={modalStyle}
      ariaHideApp={false}
    >
      {context.isOpen && context.selectedObjectIndex != null && (
        <>
          <div
            style={{
              position: "absolute",
              left: "0",
              right: "0",
              top: "0",
              bottom: "0",
              zIndex: 1,
            }}
          >
            <Preview object={context.objects[context.selectedObjectIndex]} />
          </div>
          <div
            style={{
              position: "absolute",
              left: "0",
              width: "30%",
              top: "20%",
              height: "60%",
              zIndex: 2,
              cursor: "w-resize",
            }}
            onClick={onPrevious}
          ></div>
          <div
            style={{
              position: "absolute",
              right: "0",
              width: "30%",
              top: "20%",
              height: "60%",
              zIndex: 2,
              cursor: "e-resize",
            }}
            onClick={onNext}
          ></div>
        </>
      )}
    </Modal>
  );
}
