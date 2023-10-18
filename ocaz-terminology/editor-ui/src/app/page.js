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

function TermTree({ terms }) {
  const table = Object.fromEntries(terms.map((term) => [term.id, term]));
  console.log({ table });

  const nestedTerms = terms.map((term) => {
    const nested = [term];
    while (nested[0].parentId != null) {
      const parent = table[nested[0].parentId];
      nested.unshift(parent);
    }
    return nested;
  });
  console.log({ nestedTerms });

  return (
    <ul>
      {nestedTerms.map((terms) => (
        <li key={terms[terms.length - 1].id}>
          {terms.map((term) => term.representatives.ja).join(" > ")}
        </li>
      ))}
    </ul>
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
      <hr />
      <TermTree terms={data.terms} />
    </>
  );
}
