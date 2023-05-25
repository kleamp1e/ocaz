"use client";

import useSWR from 'swr';

async function find({ }) {
  const params = {
    collection: "object",
    condition: JSON.stringify({}),
    projection: JSON.stringify({"_id":1}),
    limit: 10,
    sort: JSON.stringify([["_id", 1]]),
  };
  const queryString = new URLSearchParams(params).toString();
  return fetch(`/api/finder/find?${queryString}`).then((response) => response.json());
}

export default function Page() {
  const { data, error } = useSWR("cond", find)
  console.log({data});
  return (<main>test</main>);
}
