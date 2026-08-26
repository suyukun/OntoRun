"""S3 演示隔离：备份/恢复 ap_anping 六库（双签写回可还原）。

演示前备份（还原双签动作的写回）：
    /opt/anaconda3/bin/python3 scripts/backup_risk_demo.py backup
演示后恢复：
    /opt/anaconda3/bin/python3 scripts/backup_risk_demo.py restore
状态查询：
    /opt/anaconda3/bin/python3 scripts/backup_risk_demo.py status

备份目录：data/des/enterprises/ap_anping/.backup/（gitignore，不入库）。
恢复会还原六库（含双签动作写回的数据），恢复后需重启后端（如有连接）。
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AP_DIR = ROOT / "data" / "des" / "enterprises" / "ap_anping"
BACKUP_DIR = AP_DIR / ".backup"
DBS = ("customer.db", "risk.db", "concentration.db", "approval.db", "project.db", "base.db")


def _do_backup() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for db in DBS:
        src = AP_DIR / db
        if src.exists():
            shutil.copy2(src, BACKUP_DIR / db)
    print(f"已备份 {len(DBS)} 库 → {BACKUP_DIR}")


def _do_restore() -> None:
    if not BACKUP_DIR.exists():
        print("无备份，跳过恢复")
        return
    for db in DBS:
        src = BACKUP_DIR / db
        if src.exists():
            shutil.copy2(src, AP_DIR / db)
    print(f"已恢复 {len(DBS)} 库（来自 {BACKUP_DIR}）")


def _do_status() -> None:
    if not BACKUP_DIR.exists():
        print("无备份")
        return
    for db in DBS:
        s = BACKUP_DIR / db
        print(f"  {db}: {'✓ 已备份 ' + str(s.stat().st_size) + 'B' if s.exists() else '✗ 无'}")


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

