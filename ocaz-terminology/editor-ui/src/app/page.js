"use client";

import useSWR from "swr";
import strftime from "strftime";

const fetcher = (url) => fetch(url).then((res) => res.json());

function TermTree({ terms }) {
  const table = Object.fromEntries(terms.map((term) => [term.id, term]));
  // console.log({ table });

  const nestedTerms = terms.map((term) => {
    const nested = [term];
    while (nested[0].parentId != null) {
      const parent = table[nested[0].parentId];
      nested.unshift(parent);
    }
    return nested;
  });
  // console.log({ nestedTerms });
  nestedTerms.sort((a, b) => {
    for ( let i = 0; i < 10; i++ ) {
      if ( a[i] != null && b[i] == null ) return +1;
      if ( a[i] == null && b[i] != null ) return -1;
      if ( a[i] > b[i] ) return +1;
      if ( a[i] < b[i] ) return -1;
    }
    return 0;
  })

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

function TermTable({ terms }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Updated At</th>
          <th>Id</th>
          <th>Parent Id</th>
          <th>Ja</th>
          <th>En</th>
        </tr>
      </thead>
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
  if (data == null) return <div>Loading...</div>;

  return (
    <>
      <h1>階層</h1>
      <TermTree terms={data.terms} />
      <h1>テーブル</h1>
      <TermTable terms={data.terms} />
    </>
  );
}
