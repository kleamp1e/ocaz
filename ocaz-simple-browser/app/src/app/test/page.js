"use client";

import useSWR from "swr";

function deleteNull(params) {
  const copied = { ...params };
  for (const key in copied) {
    if (copied.hasOwnProperty(key) && copied[key] === null) {
      delete copied[key];
    }
  }
  return copied;
}

async function find({
  collection,
  condition,
  projection = null,
  sort = null,
  limit = null,
  skip = null,
}) {
  const params = {
    collection,
    condition: condition && JSON.stringify(condition),
    projection: projection && JSON.stringify(projection),
    sort: sort && JSON.stringify(sort),
    limit: limit && String(limit),
    skip: skip && String(skip),
  };
  const queryString = new URLSearchParams(deleteNull(params)).toString();
  return fetch(`/api/finder/find?${queryString}`).then((response) =>
    response.json()
  );
}

async function findObject(condition) {
  return find({
    collection: "object",
    condition: condition,
    limit: 10,
    sort: [["_id", 1]],
  });
}

export default function Page() {
  const { data, error } = useSWR({ mimeType: "image/png" }, findObject);
  console.log({ data, error });
  return <main>test</main>;
}
