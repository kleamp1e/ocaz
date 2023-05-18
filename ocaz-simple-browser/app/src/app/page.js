"use client";

import { useState, useEffect } from "react";

export default function Page() {
  const [objects, setObjects] = useState([]);

  useEffect(() => {
    async function fetchObjects() {
      const { objects } = await (await fetch("/api/objects")).json();
      setObjects(objects);
    }
    fetchObjects();
  }, []);

  console.log({ objects });

  return (
    <main>
      <table>
        <tbody>
          {objects.map((object) => (
            <tr key={object.head10mbSha1}>
              <td>
                {object.head10mbSha1}
                <img
                  src={`/api/forwarder/object/head10mbSha1/${object.head10mbSha1}`}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
