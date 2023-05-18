"use client";

import { useState, useEffect } from "react";

function VideoThumbnail({ object }) {
  return (
    <video
      src={`/api/videoDigester/object/head10mbSha1/${object.head10mbSha1}`}
      onMouseOver={(e) => e.target.play()}
      onMouseOut={(e) => e.target.pause()}
    />
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

  console.log({ objects });

  /*
                <img
                  src={`/api/forwarder/object/head10mbSha1/${object.head10mbSha1}`}
                />
  */

  return (
    <main>
      <table>
        <tbody>
          {objects.map((object) => (
            <tr key={object.head10mbSha1}>
              <td>
                {object.head10mbSha1}
                <VideoThumbnail object={object} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
