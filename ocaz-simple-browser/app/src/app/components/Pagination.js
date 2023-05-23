function PageLink({ isActive, page, setPage, children }) {
  const onClick = (e) => {
    e.preventDefault();
    setPage(page);
  };
  return (
    <span style={{ margin: "0em 0.1em" }}>
      {isActive ? (
        <a style={{ cursor: "pointer" }} onClick={onClick}>
          {children}
        </a>
      ) : (
        children
      )}
    </span>
  );
}

export default function Pagination({ page, setPage, numberOfPages }) {
  const pageSet = new Set([
    1,
    2,
    3,
    page - 2,
    page - 1,
    page,
    page + 1,
    page + 2,
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
    <div style={{ fontSize: "26px" }}>
      <PageLink isActive={page > 1} page={page - 1} setPage={setPage}>
        {"<<<"}
      </PageLink>
      {pageArray.map((p) =>
        p == null ? (
          "..."
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
    </div>
  );
}
