import type { SessionItem } from '../types';

interface Props {
  sessions: SessionItem[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onRename: (id: string) => void;
  onTogglePin: (id: string) => void;
  onToggleStar: (id: string) => void;
  onDelete: (id: string) => void;
}

/** 会话栏（左 230px）：会话列表 + 新对话 + 四操作（§3.5；T4 接 /api/sessions，服务端已排序，此处仅置顶优先稳定分组）。 */
export function SessionBar(props: Props) {
  const sorted = [...props.sessions].sort((a, b) => Number(b.pinned) - Number(a.pinned));
  return (
    <aside className="side">
      <button className="newchat" onClick={props.onNew}>
        ＋ 新对话
      </button>
      <h3>会话</h3>
      <div className="hlist">
        {sorted.map((s) => (
          <div key={s.id} className={'hitem' + (s.id === props.activeId ? ' active' : '')} onClick={() => props.onSelect(s.id)}>
            {s.starred ? '⭐ ' : null}
            {s.pinned ? '📌 ' : null}
            {s.title}
            <span className="ops">
              <button className="opbtn" title="重命名" onClick={(e) => { e.stopPropagation(); props.onRename(s.id); }}>
                ✏️
              </button>
              <button className="opbtn" title="置顶" onClick={(e) => { e.stopPropagation(); props.onTogglePin(s.id); }}>
                📌
              </button>
              <button className="opbtn" title="收藏" onClick={(e) => { e.stopPropagation(); props.onToggleStar(s.id); }}>
                ⭐
              </button>
              <button className="opbtn" title="删除" onClick={(e) => { e.stopPropagation(); props.onDelete(s.id); }}>
                🗑
              </button>
            </span>
          </div>
        ))}
      </div>
    </aside>
  );
}
