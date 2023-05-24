"use client";

import Modal from "react-modal";
import { useState } from "react";

import styles from "./PreviewModal.module.css";
import Preview from "./Preview";

const modalStyle = {
  overlay: { backgroundColor: "rgba(0, 0, 0, 0.7)" },
  content: { backgroundColor: "rgba(0, 0, 0, 0.5)" },
};
const modalStyleInfo = {
  overlay: { backgroundColor: "rgba(0, 0, 0, 0.7)" },
  content: {
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    top: "80px",
    left: "80px",
    bottom: "80px",
    right: "80px",
  },
};

export default function PreviewModal({
  isOpen,
  onRequestClose,
  onPrevious,
  onNext,
  object,
}) {
  const [isInfoOpen, setInfoOpen] = useState(false);

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      style={modalStyle}
      ariaHideApp={false}
    >
      {isOpen && object && (
        <>
          <div className={styles.main}>
            <Preview object={object} />
          </div>
          <div className={styles.previous} onClick={onPrevious}></div>
          <div className={styles.next} onClick={onNext}></div>
          <div className={styles.close} onClick={onRequestClose}>
            x
          </div>
          <div className={styles.info} onClick={() => setInfoOpen(true)}>
            i
          </div>
          <Modal
            isOpen={isInfoOpen}
            onRequestClose={() => setInfoOpen(false)}
            style={modalStyleInfo}
            ariaHideApp={false}
          >
            {isInfoOpen && object && (
              <pre style={{ fontSize: "1.3rem", fontFamily: "monospace" }}>
                {JSON.stringify(object, null, 2)}
              </pre>
            )}
          </Modal>
        </>
      )}
    </Modal>
  );
}
