#!/usr/bin/env python3
import sys
import time

try:
    import pyautogui
except ImportError:
    print("pyautoguiをインストールしてください: pip install pyautogui")
    sys.exit(1)


def interactive_mode():
    print("=" * 50)
    print("キャプチャ範囲設定ツール")
    print("=" * 50)
    print("\n3秒後に座標取得を開始します...")
    print("マウスをキャプチャしたい領域の【左上】に移動してください")
    time.sleep(3)
    
    x1, y1 = pyautogui.position()
    print(f"\n左上座標: ({x1}, {y1})")
    
    print("\n3秒以内にマウスを【右下】に移動してください...")
    time.sleep(3)
    
    x2, y2 = pyautogui.position()
    print(f"右下座標: ({x2}, {y2})")
    
    width = x2 - x1
    height = y2 - y1
    
    print("\n" + "=" * 50)
    print("config.json に設定する値:")
    print("=" * 50)
    print(f'"capture_region": {{')
    print(f'    "x": {x1},')
    print(f'    "y": {y1},')
    print(f'    "width": {width},')
    print(f'    "height": {height}')
    print(f'}}')
    print(f"\n範囲: ({x1}, {y1}) から ({x2}, {y2})")
    print(f"サイズ: {width} x {height} ピクセル")


if __name__ == "__main__":
    interactive_mode()