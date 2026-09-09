import { useEffect, useRef, useState, type ReactNode } from 'react';
import { Icon } from './Icon';
import type { SessionItem } from '../types';

interface Props {
  sessions: SessionItem[];
  archivedSessions: SessionItem[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onRename: (id: string) => void;
  onTogglePin: (id: string) => void;
  onToggleStar: (id: string) => void;
  onArchive: (id: string) => void;
  onRestore: (id: string) => void;
  onDelete: (id: string) => void;
}

/** 时间分组标签（今天/昨天/7 天内/更早）；解析失败归「更早」 */
function groupLabel(updatedAt?: string): string {
  if (!updatedAt) return '更早';
  const d = new Date(updatedAt.includes('T') ? updatedAt : updatedAt.replace(' ', 'T'));
  if (Number.isNaN(d.getTime())) return '更早';
  const dayMs = 86400000;
  const diff = (new Date(new Date().toDateString()).getTime() - new Date(d.toDateString()).getTime()) / dayMs;
  if (diff <= 0) return '今天';
  if (diff === 1) return '昨天';
  if (diff < 7) return '7 天内';
  return '更早';
}

/** 置顶组 + 时间组稳定排序 */
const GROUP_ORDER = ['今天', '昨天', '7 天内', '更早'];

interface Group {
  label: string;
  items: SessionItem[];
}

function buildGroups(sessions: SessionItem[]): Group[] {
  const pinned = sessions.filter((s) => s.pinned);
  const groups: Group[] = [];
  if (pinned.length > 0) groups.push({ label: '置顶', items: pinned });
  const byLabel = new Map<string, SessionItem[]>();
  for (const s of sessions.filter((x) => !x.pinned)) {
    const label = groupLabel(s.updatedAt);
    const bucket = byLabel.get(label) ?? [];
    bucket.push(s);
    byLabel.set(label, bucket);
  }
  for (const label of GROUP_ORDER) {
    const items = byLabel.get(label);
    if (items && items.length > 0) groups.push({ label, items });
  }
  return groups;
}

/**
 * 会话栏（左 230px）：新对话 + 时间分组列表 + 底部归档区（§3.5；T4 接 /api/sessions）。
 * hover 露出快捷置顶 + ⋯ 菜单（重命名/置顶/收藏/归档/删除）；归档区可恢复或彻底删除。
 * 菜单项纯文字（UX 报告 §三 文字优先原则）。
 */
export function SessionBar(props: Props) {
  const [menuFor, setMenuFor] = useState<string | null>(null);
  const [archOpen, setArchOpen] = useState(false);
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

  const groups = buildGroups(props.sessions);
  const closeMenu = () => setMenuFor(null);

  const item = (s: SessionItem, ops: ReactNode) => (
    <div
      key={s.id}
      className={'hitem' + (s.id === props.activeId ? ' active' : '') + (menuFor === s.id ? ' menu-open' : '')}
      onClick={() => props.onSelect(s.id)}
    >
      {s.starred && <Icon name="star" size={12} filled className="hflag" />}
      {s.pinned && <Icon name="pin" size={12} className="hflag" />}
      {s.title}
      <span className="ops">{ops}</span>
    </div>
  );

  return (
    <aside className="side">
      <button className="newchat" onClick={props.onNew}>
        <Icon name="plus" size={14} /> 新对话
      </button>
      <div className="hlist">
        {groups.map((g) => (
          <div key={g.label}>
            <h3>{g.label}</h3>
            {g.items.map((s) =>
              item(
                s,
                menuFor === s.id ? (
                  <div className="sessionmenu" ref={menuRef}>
                    <button onClick={(e) => { e.stopPropagation(); closeMenu(); props.onRename(s.id); }}>重命名</button>
                    <button onClick={(e) => { e.stopPropagation(); closeMenu(); props.onTogglePin(s.id); }}>
                      {s.pinned ? '取消置顶' : '置顶'}
                    </button>
                    <button onClick={(e) => { e.stopPropagation(); closeMenu(); props.onToggleStar(s.id); }}>
                      {s.starred ? '取消收藏' : '收藏'}
                    </button>
                    <button onClick={(e) => { e.stopPropagation(); closeMenu(); props.onArchive(s.id); }}>归档</button>
                    <button className="danger" onClick={(e) => { e.stopPropagation(); closeMenu(); props.onDelete(s.id); }}>删除</button>
                  </div>
                ) : (
                  <>
                    <button
                      className="opbtn"
                      title={s.pinned ? '取消置顶' : '置顶'}
                      aria-label={s.pinned ? '取消置顶' : '置顶'}
                      onClick={(e) => { e.stopPropagation(); props.onTogglePin(s.id); }}
                    >
                      <Icon name="pin" size={13} />
                    </button>
                    <button
                      className="opbtn"
                      title="更多操作"
                      aria-label="更多操作"
                      onClick={(e) => { e.stopPropagation(); setMenuFor(s.id); }}
                    >
                      <Icon name="more" size={14} />
                    </button>
                  </>
                ),
              ),
            )}
          </div>
        ))}
      </div>
      {props.archivedSessions.length > 0 && (
        <div className="arch">
          <button className="arch-toggle" onClick={() => setArchOpen((v) => !v)} aria-expanded={archOpen}>
            <Icon name="archive" size={12} /> 已归档 · {props.archivedSessions.length}
            <Icon name="chevron-down" size={11} className={'arch-chev' + (archOpen ? ' open' : '')} />
          </button>
          {archOpen && (
            <div className="arch-list">
              {props.archivedSessions.map((s) => (
                <div key={s.id} className="arch-item">
                  <span className="arch-title">{s.title}</span>
                  <span className="ops">
                    <button className="opbtn" title="恢复到会话列表" onClick={() => props.onRestore(s.id)}>
                      <Icon name="rotate" size={12} />
                    </button>
                    <button className="opbtn" title="彻底删除" onClick={() => props.onDelete(s.id)}>
                      <Icon name="trash" size={12} />
                    </button>
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </aside>
  );
}
