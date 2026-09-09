import type { SessionItem } from '../types';

interface Props {
  sessions: SessionItem[];
  activeId: number;
  onSelect: (id: number) => void;
  onNew: () => void;
  onRename: (id: number) => void;
  onTogglePin: (id: number) => void;
  onToggleStar: (id: number) => void;
  onDelete: (id: number) => void;
}

/** 会话栏（左 230px）：会话列表 + 新对话 + 四操作（§3.5；本任务为本地态占位，服务端持久化在 T4）。 */
export function SessionBar(props: Props) {
  const sorted = [...props.sessions].sort((a, b) => Number(b.pinned) - Number(a.pinned) || b.id - a.id);
  return (
    <aside className="side">
      <button className="newchat" onClick={props.onNew}>
        ＋ 新对话
      </button>
      <h3>会话</h3>
      <div className="hlist">
        {sorted.map((s) => (
          <div key={s.id} className={'hitem' + (s.id === props.activeId ? ' active' : '')} onClick={() => props.onSelect(s.id)}>
            {s.starred ? '⭐ ' : ''}
            {s.pinned ? '📌 ' : ''}
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
