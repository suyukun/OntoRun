interface Props {
  rows: Record<string, unknown>[];
}

/** 数据区表格：列由 rows 首行键推导（与图表同源同一 rows——D7）；React 转义渲染，禁 innerHTML。 */
export function DataTable({ rows }: Props) {
  const cols = Object.keys(rows[0] ?? {});
  return (
    <table>
      <thead>
        <tr>
          {cols.map((c) => (
            <th key={c}>{c}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={i}>
            {cols.map((c) => (
              <td key={c}>{String(r[c])}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
