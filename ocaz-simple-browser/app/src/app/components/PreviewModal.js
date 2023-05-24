"use client";

import Modal from "react-modal";
import { useState } from "react";

import styles from "./PreviewModal.module.css";
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
  const [isInfoOpen, setInfoOpen] = useState(false);

  return (
    <Modal
      isOpen={isOpen}
      onRequestClose={onRequestClose}
      style={modalStyle}
      ariaHideApp={false}
    >
      {context.isOpen && context.selectedObjectIndex != null && (
        <>
          <div className={styles.main}>
            <Preview object={context.objects[context.selectedObjectIndex]} />
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
            style={modalStyle}
            ariaHideApp={false}
          >
            <div>info</div>
          </Modal>
        </>
      )}
    </Modal>
  );
}
