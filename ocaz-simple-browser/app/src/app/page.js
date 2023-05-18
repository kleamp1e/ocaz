"use client";

import styles from "./page.module.css";
import { useState, useEffect } from "react";

export default function Home() {
  const [objects, setObjects] = useState([]);

  useEffect(() => {
    console.log("useEffect");
    async function fetchObjects() {
      const { objects } = await (await fetch("/api/objects")).json();
      setObjects(objects);
    }
    fetchObjects();
  }, []);

  console.log({ objects });

  return <main className={styles.main}>Root</main>;
}
