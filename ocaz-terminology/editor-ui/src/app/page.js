"use client";

import useSWR from "swr";
import strftime from "strftime";

const fetcher = (url) => fetch(url).then((res) => res.json());

function TermTable({ terms }) {
  return (
    <table>
      <tbody>
        {terms.map((term) => (
          <tr key={term.id}>
            <td className="border">
              {strftime("%Y-%m-%dT%H:%M:%S", new Date(term.updatedAt * 1000))}
            </td>
            <td className="border">{term.id}</td>
            <td className="border">{term.parentId ?? "-"}</td>
            <td className="border">{term.representatives?.ja ?? "-"}</td>
            <td className="border">{term.representatives?.en ?? "-"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function Page() {
  const { data, error, isLoading } = useSWR(
    "http://localhost:8000/terms",
    fetcher
  );
  console.log({ data });
  if (data == null) return <div>Loading...</div>;

  return (
    <>
      <TermTable terms={data.terms} />
    </>
  );
}
