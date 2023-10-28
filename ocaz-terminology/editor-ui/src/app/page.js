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
import { Input } from "@nextui-org/react";

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
        const response = await addTerm({
          parentId: id,
          representativeJa: trimmed,
        });
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

function SynonymEditButton({ terms, id }) {
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const { mutate } = useSWRConfig();
  const term = _.find(terms, (term) => term.id == id);
  const synonyms = term?.synonyms ?? [];
  const [editingSynonyms, setEditingSynonyms] = useState(
    JSON.stringify(synonyms)
  );

  const save = async (onClose) => {
    const response = await setSynonyms({
      id,
      synonyms: JSON.parse(editingSynonyms),
    });
    console.log({ response });
    mutate("http://localhost:8000/terms");
    onClose();
  };

  return (
    <>
      <Button size="sm" className="ml-1" onPress={onOpen}>
        同義語を編集
      </Button>
      <Modal size="lg" isOpen={isOpen} onOpenChange={onOpenChange}>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">
                同義語を編集 (ID: {id ?? "-"} / ja:{" "}
                {term?.representatives?.ja ?? "-"})
              </ModalHeader>
              <ModalBody>
                <Button
                  size="sm"
                  onPress={() => {
                    setEditingSynonyms(JSON.stringify([{ ja: "" }]));
                  }}
                >
                  テンプレートja
                </Button>
                <Textarea
                  className="max-w-xs"
                  value={editingSynonyms ?? ""}
                  onChange={(e) => setEditingSynonyms(e.target.value)}
                />
              </ModalBody>
              <ModalFooter>
                <Button color="primary" onPress={() => save(onClose)}>
                  保存
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
}

function TermTree({ nestedTerms }) {
  const [keyword, setKeyword] = useState("");

  const filteredNestedTerms = nestedTerms.filter((terms) => {
    if (keyword == "") return true;
    for (const term of terms) {
      if ((term?.representatives?.ja ?? "").includes(keyword)) return true;
      if ((term?.representatives?.en ?? "").includes(keyword)) return true;
      for (const synonym of term?.synonyms ?? []) {
        if ((synonym?.ja ?? "").includes(keyword)) return true;
        if ((synonym?.en ?? "").includes(keyword)) return true;
      }
    }
    return false;
  });

  return (
    <>
      <div>
        <Input
          type="text"
          label="検索キーワード"
          isClearable={true}
          value={keyword}
          onValueChange={setKeyword}
        />
      </div>
      <ul>
        {filteredNestedTerms.map((terms) => (
          <li key={terms[terms.length - 1].id} className="my-1">
            <RepresentativeAddButton
              terms={terms}
              id={terms[terms.length - 1].id}
            />
            <SynonymEditButton terms={terms} id={terms[terms.length - 1].id} />
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
    </>
  );
}

function TermTable({ terms }) {
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
            <td className="border cursor-pointer">
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

export default function Page() {
  const { data, error, isLoading } = useSWR(
    "http://localhost:8000/terms",
    fetcher
  );
  if (data == null) return <div>Loading...</div>;

  const terms = data.terms;
  const table = Object.fromEntries(terms.map((term) => [term.id, term]));
  const nestedTerms = terms.map((term) => {
    const nested = [term];
    while (nested[0].parentId != null) {
      const parent = table[nested[0].parentId];
      nested.unshift(parent);
    }
    return nested;
  });
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

  return (
    <NextUIProvider>
      <h1>階層 ({data.terms.length})</h1>
      <TermTree nestedTerms={nestedTerms} />
      <h1>テーブル</h1>
      <TermTable terms={data.terms} />
    </NextUIProvider>
  );
}
