"use client";

import _ from "lodash";
import { Button } from "@nextui-org/react";
import { Textarea } from "@nextui-org/react";
import { NextUIProvider } from "@nextui-org/react";
import { useState } from "react";
import strftime from "strftime";
import useSWR, { useSWRConfig } from "swr";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
} from "@nextui-org/react";

const fetcher = (url) => fetch(url).then((res) => res.json());

function RepresentativeAddButton({ terms, id }) {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [representativeJaLines, setRepresentativeJaLines] = useState("");
  const { mutate } = useSWRConfig();
  const term = _.find(terms, (term) => term.id == id);

  const add = async (onClose) => {
    for (const representativeJa of representativeJaLines.split("\n")) {
      const trimmed = representativeJa.trim();
      if (trimmed != "") {
        const response = await addTerm({ parentId: id, representativeJa: trimmed });
        console.log({ response });
      }
    }
    mutate("http://localhost:8000/terms");
    setRepresentativeJaLines("");
    onClose();
  };

  return (
    <>
      <Button size="sm" className="ml-1" onPress={onOpen}>
        代表語を追加
      </Button>
      <Modal size="lg" isOpen={isOpen} onOpenChange={onOpenChange}>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">
                代表語を追加
              </ModalHeader>
              <ModalBody>
                <div>ID: {id ?? "-"}</div>
                <div>ja: {term?.representatives?.ja ?? "-"}</div>
                <div>
                  <Textarea
                    className="max-w-xs"
                    value={representativeJaLines}
                    onChange={(e) => setRepresentativeJaLines(e.target.value)}
                  />
                </div>
              </ModalBody>
              <ModalFooter>
                <Button color="primary" onPress={() => add(onClose)}>
                  追加
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
}

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
      const aJa = a[i]?.representatives?.ja;
      const bJa = b[i]?.representatives?.ja;
      if (aJa != null && bJa == null) return +1;
      if (aJa == null && bJa != null) return -1;
      if (aJa > bJa) return +1;
      if (aJa < bJa) return -1;
    }
    return 0;
  });

  /*
          <Button size="sm" className="ml-1">
            同義語を編集
          </Button>
*/

  return (
    <ul>
      {nestedTerms.map((terms) => (
        <li
          key={terms[terms.length - 1].id}
          className="cursor-pointer my-1"
          onClick={() => setId(terms[terms.length - 1].id)}
        >
          <RepresentativeAddButton
            terms={terms}
            id={terms[terms.length - 1].id}
          />
          <span className="ml-1">
            {terms
              .map((term) => {
                const synonyms = (term?.synonyms ?? [])
                  .map((s) => s?.ja)
                  .filter((s) => s != null);
                return (
                  term?.representatives?.ja +
                  (synonyms.length == 0 ? "" : ` (${synonyms.join(", ")})`)
                );
              })
              .join(" > ")}
          </span>
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
          <th>ID</th>
          <th>Parent ID</th>
          <th>Representatives</th>
          <th>Synonyms</th>
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
              {JSON.stringify(term.representatives)}
            </td>
            <td className="border">{JSON.stringify(term.synonyms ?? [])}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

async function addTerm({
  id = null,
  parentId = null,
  representativeJa = null,
  representativeEn = null,
}) {
  return await fetch("http://localhost:8000/term/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      id,
      parentId,
      representativeJa,
      representativeEn,
    }),
  });
}

async function setSynonyms({ id, synonyms }) {
  return await fetch(`http://localhost:8000/term/id/${id}/synonyms`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      synonyms: synonyms.map((synonym) =>
        _.defaults(synonym, { ja: null, en: null })
      ),
    }),
  });
}

function EditSynonyms({ terms, id }) {
  const [editingSynonyms, setEditingSynonyms] = useState(null);
  const { mutate } = useSWRConfig();

  const term = _.find(terms, (term) => term.id == id);
  const synonyms = term?.synonyms ?? [];
  const langs = ["ja", "en"];

  const save = async () => {
    const response = await setSynonyms({
      id,
      synonyms: JSON.parse(editingSynonyms),
    });
    console.log({ response });
    mutate("http://localhost:8000/terms");
    setEditingSynonyms(null);
  };

  return (
    <div className="m-2">
      <div>ID: {id}</div>
      <div>Synonyms: {JSON.stringify(synonyms)}</div>
      <table>
        <thead>
          <tr>
            <th className="border">Index</th>
            {langs.map((lang) => (
              <th key={lang} className="border">
                {lang}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {synonyms.map((synonym, index) => (
            <tr key={index}>
              <td className="border">{index}</td>
              {langs.map((lang) => (
                <td key={lang} className="border">
                  {synonym[lang] ?? "-"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div>
        <Button
          color="primary"
          onClick={() => {
            setEditingSynonyms(JSON.stringify(synonyms));
          }}
        >
          編集
        </Button>
        <Button
          color="primary"
          onClick={() => {
            setEditingSynonyms(JSON.stringify([{ ja: "" }]));
          }}
        >
          テンプレートを使って編集
        </Button>
      </div>
      {editingSynonyms != null && (
        <>
          <div>
            <Textarea
              className="max-w-xs"
              value={editingSynonyms ?? ""}
              onChange={(e) => setEditingSynonyms(e.target.value)}
            />
          </div>
          <div>
            <Button color="primary" onClick={save}>
              保存
            </Button>
          </div>
        </>
      )}
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
    <NextUIProvider>
      <h1>同義語</h1>
      <EditSynonyms terms={data.terms} id={parentId} />
      <h1>階層 ({data.terms.length})</h1>
      <TermTree terms={data.terms} setId={setParentId} />
      <h1>テーブル</h1>
      <TermTable terms={data.terms} setId={setParentId} />
    </NextUIProvider>
  );
}
