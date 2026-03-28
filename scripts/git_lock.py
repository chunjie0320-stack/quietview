"""
git_lock.py — 全局 git 操作文件锁
所有需要 git add/commit/push 的脚本都应通过此模块操作

用法：
    from git_lock import git_push_with_lock
    git_push_with_lock(repo_dir, commit_msg, files_to_add)
"""

import subprocess
import time
import os
import sys

LOCK_FILE = "/tmp/quietview_git.lock"
LOCK_TIMEOUT = 120  # 最多等120秒
LOCK_STALE = 180    # 锁文件超过180秒视为僵尸锁，强制清除


def _acquire_lock(timeout=LOCK_TIMEOUT):
    """抢锁，返回True表示成功"""
    deadline = time.time() + timeout
    pid = os.getpid()
    script = os.path.basename(sys.argv[0]) if sys.argv else "unknown"

    while time.time() < deadline:
        # 检查是否有僵尸锁
        if os.path.exists(LOCK_FILE):
            try:
                mtime = os.path.getmtime(LOCK_FILE)
                if time.time() - mtime > LOCK_STALE:
                    print(f"  ⚠️ 发现僵尸锁（{int(time.time()-mtime)}秒前），强制清除", file=sys.stderr)
                    os.remove(LOCK_FILE)
            except Exception:
                pass

        # 尝试原子创建锁文件
        try:
            fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, 'w') as f:
                f.write(f"{pid}\n{script}\n{time.time()}\n")
            return True
        except FileExistsError:
            # 锁被占用，等待
            try:
                with open(LOCK_FILE) as f:
                    content = f.read().strip().split('\n')
                    holder = content[1] if len(content) > 1 else "unknown"
            except Exception:
                holder = "unknown"
            print(f"  ⏳ git锁被 [{holder}] 占用，等待...", file=sys.stderr)
            time.sleep(5)

    return False


def _release_lock():
    """释放锁"""
    try:
        os.remove(LOCK_FILE)
    except Exception:
        pass


def git_push_with_lock(repo_dir, commit_msg, files_to_add=None, dry_run=False):
    """
    安全的 git add + commit + pull --rebase + push
    使用全局文件锁防止并发冲突

    Args:
        repo_dir: git仓库路径
        commit_msg: commit消息
        files_to_add: 要add的文件列表，None表示 git add -A
        dry_run: True时跳过实际push
    """
    if dry_run:
        print(f"  [dry-run] 跳过 git push: {commit_msg}", file=sys.stderr)
        return

    if not _acquire_lock():
        raise RuntimeError(f"⛔ 无法获取 git 锁（超时 {LOCK_TIMEOUT}s），放弃 push: {commit_msg}")

    try:
        print(f"  🔒 获得 git 锁，开始推送: {commit_msg}", file=sys.stderr)

        # git add
        if files_to_add:
            for f in files_to_add:
                subprocess.run(['git', 'add', f], cwd=repo_dir, check=True)
        else:
            subprocess.run(['git', 'add', '-A'], cwd=repo_dir, check=True)

        # 检查是否有变更
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=repo_dir)
        if result.returncode == 0:
            print(f"  ℹ️ 无变更，跳过 commit: {commit_msg}", file=sys.stderr)
            return

        # git commit
        subprocess.run(['git', 'commit', '-m', commit_msg], cwd=repo_dir, check=True)

        # pull --rebase（防止并发push时的远端更新）
        result = subprocess.run(
            ['git', 'pull', '--rebase', 'origin', 'main'],
            cwd=repo_dir, capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  ⚠️ pull --rebase 有问题: {result.stderr[:200]}", file=sys.stderr)
            # 尝试 abort rebase 后强推（极端情况）
            subprocess.run(['git', 'rebase', '--abort'], cwd=repo_dir)
            subprocess.run(['git', 'push', '--force-with-lease'], cwd=repo_dir, check=True)
            return

        # git push
        subprocess.run(['git', 'push'], cwd=repo_dir, check=True)
        print(f"  ✅ git push 完成: {commit_msg}", file=sys.stderr)

    finally:
        _release_lock()
        print(f"  🔓 git 锁已释放", file=sys.stderr)
