"use client";

import useSWR from "swr";
import strftime from "strftime";
import { useState } from "react";

const fetcher = (url) => fetch(url).then((res) => res.json());

function TermTree({ terms, setId }) {
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
    for (let i = 0; i < 10; i++) {
      if (a[i] != null && b[i] == null) return +1;
      if (a[i] == null && b[i] != null) return -1;
      if (a[i] > b[i]) return +1;
      if (a[i] < b[i]) return -1;
    }
    return 0;
  });

  return (
    <ul>
      {nestedTerms.map((terms) => (
        <li
          key={terms[terms.length - 1].id}
          className="cursor-pointer"
          onClick={() => setId(terms[terms.length - 1].id)}
        >
          {terms.map((term) => term.representatives.ja).join(" > ")}
        </li>
      ))}
    </ul>
  );
}

function TermTable({ terms, setId }) {
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
            <td
              className="border cursor-pointer"
              onClick={() => setId(term.id)}
            >
              {term.representatives?.ja ?? "-"}
            </td>
            <td className="border">{term.representatives?.en ?? "-"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function AddTermForm({ terms, parentId }) {
  return (
    <div>
      <div>Parent ID: {parentId ?? "-"}</div>
    </div>
  );
}

export default function Page() {
  const [parentId, setParentId] = useState(null);
  const { data, error, isLoading } = useSWR(
    "http://localhost:8000/terms",
    fetcher
  );
  if (data == null) return <div>Loading...</div>;

  return (
    <>
      <h1>追加</h1>
      <AddTermForm parentId={parentId} />
      <h1>階層</h1>
      <TermTree terms={data.terms} setId={setParentId} />
      <h1>テーブル</h1>
      <TermTable terms={data.terms} setId={setParentId} />
    </>
  );
}
