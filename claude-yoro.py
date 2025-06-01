import pexpect
import sys
import re
import threading

def monitor_and_auto_select(child):
    buffer = ""
    while True:
        try:
            # 画面出力を少しずつ読む
            out = child.read_nonblocking(size=1024, timeout=0.1)
            if out:
                sys.stdout.write(out)
                sys.stdout.flush()
                buffer += out

                # 質問パターンを検出
                if re.search(r'Do you trust the files in this folder\?', buffer):
                    # 選択肢を抽出
                    choices = re.findall(r'([❯ ] )([^\n]+)', buffer)
                    yes_idx = None
                    for i, (_, choice) in enumerate(choices):
                        if choice.strip().lower().startswith('yes'):
                            yes_idx = i
                            break
                    if yes_idx is not None:
                        current_idx = next((i for i, (mark, _) in enumerate(choices) if '❯' in mark), 0)
                        move = yes_idx - current_idx
                        key = '\033[B' if move > 0 else '\033[A'
                        for _ in range(abs(move)):
                            child.send(key)
                        child.send('\r')
                        buffer = ""  # バッファをクリア
            if not child.isalive():
                break
        except pexpect.exceptions.TIMEOUT:
            continue
        except pexpect.exceptions.EOF:
            break

def forward_stdin(child):
    # ユーザーのキーボード入力をclaudeに転送
    while child.isalive():
        try:
            c = sys.stdin.read(1)
            if c:
                child.send(c)
        except Exception:
            break

if __name__ == "__main__":
    # claudeコマンドに置き換えてください
    cmd = "claude [コマンドや引数]"
    child = pexpect.spawn(cmd, encoding='utf-8')

    # 標準入力を転送するスレッド
    t_stdin = threading.Thread(target=forward_stdin, args=(child,), daemon=True)
    t_stdin.start()

    # 出力監視＆自動選択
    monitor_and_auto_select(child)
