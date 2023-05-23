import styles from "./Pagination.module.css";

function PageLink({ isActive, page, setPage, children }) {
  const onClick = (e) => {
    e.preventDefault();
    setPage(page);
  };
  return (
    <li className={isActive ? styles.active : styles.inactive}>
      {isActive ? <a onClick={onClick}>{children}</a> : children}
    </li>
  );
}

function Snip() {
  return <li className={styles.snip}>...</li>;
}

export function PaginationContent({ children }) {
  return <div className={styles.content}>{children}</div>;
}

export function Pagination({ page, setPage, numberOfPages }) {
  const pageSet = new Set([
    1,
    2,
    3,
    4,
    page - 3,
    page - 2,
    page - 1,
    page,
    page + 1,
    page + 2,
    page + 3,
    numberOfPages - 3,
    numberOfPages - 2,
    numberOfPages - 1,
    numberOfPages,
  ]);
  const pageArray = Array.from(pageSet)
    .sort((a, b) => a - b)
    .filter((p) => p >= 1)
    .filter((p) => p <= numberOfPages)
    .reduce((memo, p) => {
      if (memo.length > 0 && memo[memo.length - 1] != p - 1) {
        memo.push(null);
      }
      memo.push(p);
      return memo;
    }, []);

  return (
    <ul className={styles.pagination}>
      <PageLink isActive={page > 1} page={page - 1} setPage={setPage}>
        {"<<<"}
      </PageLink>
      {pageArray.map((p) =>
        p == null ? (
          <Snip />
        ) : (
          <PageLink key={p} isActive={p != page} page={p} setPage={setPage}>
            {p}
          </PageLink>
        )
      )}
      <PageLink
        isActive={page < numberOfPages}
        page={page + 1}
        setPage={setPage}
      >
        {">>>"}
      </PageLink>{" "}
    </ul>
  );
}
