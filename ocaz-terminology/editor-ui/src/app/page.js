"use client"

import useSWR from "swr";

const fetcher = (url) => fetch(url).then((res) => res.json());

export default function Page() {
  const { data, error, isLoading } = useSWR(
    "http://localhost:8000/terms",
    fetcher
  );
  console.log({ data });
  return <></>;
}
