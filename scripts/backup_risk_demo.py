"""S3 演示隔离：备份/恢复 ap_anping 六库 + 本体库（双签写回/published 终态可还原）。

演示前备份（还原双签动作的写回）：
    /opt/anaconda3/bin/python3 scripts/backup_risk_demo.py backup
演示后恢复：
    /opt/anaconda3/bin/python3 scripts/backup_risk_demo.py restore
状态查询：
    /opt/anaconda3/bin/python3 scripts/backup_risk_demo.py status

备份目录：data/des/enterprises/ap_anping/.backup/ 与 data/ontology/.backup/（均 gitignore，不入库）。
本体库组含 published 终态唯一回退手段（s3_risk_ontology.db 为 S3 风险本体 33+37 真相源；
ontology.db 为 S1 零售运行时库），E4 状态机无 unpublish，回退只能靠文件还原。
恢复会还原全部库，恢复后需重启后端（如有连接）。
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# (源目录, 备份目录, 库文件名列表) —— 六库（ap_anping 源系统）+ 本体两库
_GROUPS: list[tuple[Path, Path, tuple[str, ...]]] = [
    (
        ROOT / "data" / "des" / "enterprises" / "ap_anping",
        ROOT / "data" / "des" / "enterprises" / "ap_anping" / ".backup",
        ("customer.db", "risk.db", "concentration.db", "approval.db", "project.db", "base.db"),
    ),
    (
        ROOT / "data" / "ontology",
        ROOT / "data" / "ontology" / ".backup",
        ("ontology.db", "s3_risk_ontology.db"),
    ),
]


def _do_backup() -> None:
    total = 0
    for src_dir, backup_dir, dbs in _GROUPS:
        backup_dir.mkdir(parents=True, exist_ok=True)
        for db in dbs:
            src = src_dir / db
            if src.exists():
                shutil.copy2(src, backup_dir / db)
                total += 1
    print(f"已备份 {total} 库 → {[_g[1] for _g in _GROUPS]}")


def _do_restore() -> None:
    total = 0
    for src_dir, backup_dir, dbs in _GROUPS:
        if not backup_dir.exists():
            continue
        for db in dbs:
            src = backup_dir / db
            if src.exists():
                shutil.copy2(src, src_dir / db)
                total += 1
    if total == 0:
        print("无备份，跳过恢复")
        return
    print(f"已恢复 {total} 库")


def _do_status() -> None:
    found = False
    for _, backup_dir, dbs in _GROUPS:
        for db in dbs:
            s = backup_dir / db
            if s.exists():
                found = True
            print(f"  {backup_dir.parent.name}/{db}: "
                  f"{'✓ 已备份 ' + str(s.stat().st_size) + 'B' if s.exists() else '✗ 无'}")
    if not found:
        print("无备份")


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "backup":
        _do_backup()
    elif cmd == "restore":
        _do_restore()
    elif cmd == "status":
        _do_status()
    else:
        print(f"未知命令: {cmd}（backup/restore/status）")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

