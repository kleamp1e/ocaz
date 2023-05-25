"use client";

import useSWR from "swr";
import { useState } from "react";

import { Pagination, PaginationContent } from "../components/Pagination";
import { find } from "../lib/finder";

function Objects({ objectIds }) {
  const { data, error } = useSWR(
    {
      collection: "object",
      condition: { _id: { $in: objectIds } },
    },
    find
  );
  console.log({ data, error });

  if (error) return <div>Error</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <ul>
      {data.records.map((object) => (
        <li key={object["_id"]}>{JSON.stringify(object)}</li>
      ))}
    </ul>
  );
}

export default function Page() {
  const [context, setContext] = useState({
    perPage: 10,
    page: 1,
    isOpen: false,
  });
  const { data, error } = useSWR(
    {
      collection: "object",
      condition: {},
      // condition: { mimeType: "image/jpeg" },
      projection: { _id: 1 },
      limit: 1000, // DEBUG:
      sort: [["_id", 1]],
    },
    find
  );
  console.log({ data, error });

  if (error) return <div>Error</div>;
  if (!data) return <div>Loading...</div>;

  const numberOfPages = Math.ceil(data.records.length / context.perPage);
  const startIndex = context.perPage * (context.page - 1);
  const endIndex = context.perPage * context.page;
  const objectIds = data.records
    .slice(startIndex, endIndex)
    .map((object) => object["_id"]);
  console.log({ numberOfPages, context });

  return (
    <main>
      <Pagination
        page={context.page}
        numberOfPages={numberOfPages}
        setPage={(page) => setContext((prev) => ({ ...prev, page }))}
      />
      <PaginationContent>
        <Objects objectIds={objectIds} />
      </PaginationContent>
    </main>
  );
}
