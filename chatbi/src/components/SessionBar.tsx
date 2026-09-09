import { useEffect, useRef, useState } from 'react';
import { Icon } from './Icon';
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

/**
 * 会话栏（左 230px）：会话列表 + 新对话 + 四操作（§3.5；T4 接 /api/sessions，服务端已排序，此处仅置顶优先稳定分组）。
 * 低频操作（重命名/置顶/收藏/删除）收进 ⋯ 菜单、菜单项纯文字（UX 报告 §三 文字优先原则）。
 */
export function SessionBar(props: Props) {
  const [menuFor, setMenuFor] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement | null>(null);

  // 菜单开启期间点击外部关闭
  useEffect(() => {
    if (!menuFor) return;
    const close = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuFor(null);
    };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, [menuFor]);

  const sorted = [...props.sessions].sort((a, b) => Number(b.pinned) - Number(a.pinned));
  const closeMenu = () => setMenuFor(null);
  return (
    <aside className="side">
      <button className="newchat" onClick={props.onNew}>
        <Icon name="plus" size={14} /> 新对话
      </button>
      <h3>会话</h3>
      <div className="hlist">
        {sorted.map((s) => (
          <div
            key={s.id}
            className={'hitem' + (s.id === props.activeId ? ' active' : '') + (menuFor === s.id ? ' menu-open' : '')}
            onClick={() => props.onSelect(s.id)}
          >
            {s.starred && <Icon name="star" size={12} filled className="hflag" />}
            {s.pinned && <Icon name="pin" size={12} className="hflag" />}
            {s.title}
            <span className="ops">
              {menuFor === s.id ? (
                <div className="sessionmenu" ref={menuRef}>
                  <button onClick={(e) => { e.stopPropagation(); closeMenu(); props.onRename(s.id); }}>重命名</button>
                  <button onClick={(e) => { e.stopPropagation(); closeMenu(); props.onTogglePin(s.id); }}>
                    {s.pinned ? '取消置顶' : '置顶'}
                  </button>
                  <button onClick={(e) => { e.stopPropagation(); closeMenu(); props.onToggleStar(s.id); }}>
                    {s.starred ? '取消收藏' : '收藏'}
                  </button>
                  <button className="danger" onClick={(e) => { e.stopPropagation(); closeMenu(); props.onDelete(s.id); }}>删除</button>
                </div>
              ) : (
                <button
                  className="opbtn"
                  title="更多操作"
                  aria-label="更多操作"
                  onClick={(e) => { e.stopPropagation(); setMenuFor(s.id); }}
                >
                  <Icon name="more" size={14} />
                </button>
              )}
            </span>
          </div>
        ))}
      </div>
    </aside>
  );
}
