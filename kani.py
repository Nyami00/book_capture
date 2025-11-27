#!/usr/bin/env python3
"""
Book Capture Tool (pyautogui版)
画面上の指定範囲をキャプチャしてPDF化
"""

import time
import json
from pathlib import Path
import pyautogui
from PIL import Image
import img2pdf
from tqdm import tqdm


def create_default_config():
    return {
        "total_pages": 208,
        "start_page": 1,
        "capture_region": {
        "x": 1564,
        "y": 186,
        "width": 1100,
        "height": 1400
        },
        "turn_method": "right",  # right, left, space, click
        "turn_delay": 0.5,
        "click_position": {"x": 800, "y": 400},
        "output_dir": "output",
        "output_filename": "book.pdf",
        "delete_screenshots": False
    }


def capture_region(region, output_path):
    """指定領域をスクリーンショット"""
    screenshot = pyautogui.screenshot(region=(
        region["x"],
        region["y"],
        region["width"],
        region["height"]
    ))
    screenshot.save(output_path)
    return output_path


def turn_page(config):
    """ページをめくる"""
    method = config.get("turn_method", "right")
    
    if method == "right":
        pyautogui.press("right")
    elif method == "left":
        pyautogui.press("left")
    elif method == "space":
        pyautogui.press("space")
    elif method == "click":
        pos = config.get("click_position", {"x": 800, "y": 400})
        pyautogui.click(pos["x"], pos["y"])
    
    time.sleep(config.get("turn_delay", 0.5))


def create_pdf(screenshots_dir, output_path, start_page, end_page):
    """画像をPDFにまとめる"""
    print("\nPDF作成中...")
    
    image_files = []
    for i in range(start_page, end_page + 1):
        img_path = screenshots_dir / f"page_{i:04d}.png"
        if img_path.exists():
            image_files.append(str(img_path))
    
    if not image_files:
        print("画像ファイルが見つかりません")
        return None
    
    with open(output_path, "wb") as f:
        f.write(img2pdf.convert(image_files))
    
    return output_path


def main():
    config_path = Path("config.json")
    
    # 設定ファイルがなければ作成
    if not config_path.exists():
        print("設定ファイルを作成しています...")
        config = create_default_config()
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"{config_path} を作成しました")
        print("\n設定ファイルを編集してから再実行してください")
        print("\n主な設定項目:")
        print("  - total_pages: 総ページ数")
        print("  - capture_region: キャプチャ範囲 (x, y, width, height)")
        print("  - turn_method: ページめくり方法 (right/left/space/click)")
        print("  - turn_delay: めくり後の待ち時間")
        return
    
    # 設定読み込み
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # 出力フォルダ準備
    output_dir = Path(config.get("output_dir", "output"))
    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    total_pages = config["total_pages"]
    start_page = config.get("start_page", 1)
    region = config["capture_region"]
    
    print("=" * 50)
    print("Book Capture Tool")
    print("=" * 50)
    print(f"総ページ数: {total_pages}")
    print(f"開始ページ: {start_page}")
    print(f"キャプチャ範囲: ({region['x']}, {region['y']}) - "
          f"({region['x'] + region['width']}, {region['y'] + region['height']})")
    print(f"めくり方法: {config.get('turn_method', 'right')}")
    print("=" * 50)
    
    print("\nブラウザで本を開き、最初のページを表示してください")
    print("※ ブラウザをアクティブにした状態でEnterを押してください")
    input("準備ができたら Enter...")
    
    # 5秒待機（ブラウザに戻る時間）
    print("\n5秒後にキャプチャ開始します。ブラウザをクリックしてください！")
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    # プレビュー
    print("\nプレビュー撮影中...")
    preview_path = screenshots_dir / "preview.png"
    capture_region(region, preview_path)
    print(f"プレビュー保存: {preview_path}")
    print("この画像を確認してください")
    
    confirm = input("続行する場合は Enter、やり直すなら 'q': ")
    if confirm.lower() == 'q':
        print("中断しました。config.jsonのcapture_regionを調整してください。")
        return
    
    # 再度待機
    print("\n5秒後にキャプチャ開始します。ブラウザをクリックしてください！")
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("キャプチャ開始！")
    print("=" * 50)
    
    start_time = time.time()
    captured_count = 0
    
    # キャプチャ実行
    with tqdm(total=total_pages - start_page + 1,
              desc="キャプチャ中",
              bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]',
              ncols=60) as pbar:
        
        for page_num in range(start_page, total_pages + 1):
            try:
                # スクリーンショット
                output_path = screenshots_dir / f"page_{page_num:04d}.png"
                capture_region(region, output_path)
                captured_count += 1
                
                # 最後のページでなければめくる
                if page_num < total_pages:
                    turn_page(config)
                
                pbar.update(1)
                
            except Exception as e:
                print(f"\nページ {page_num} でエラー: {e}")
                retry = input("続行は Enter、中断は 'q': ")
                if retry.lower() == 'q':
                    break
    
    elapsed = time.time() - start_time
    print(f"\nキャプチャ完了: {captured_count}ページ ({elapsed:.1f}秒)")
    
    # PDF作成
    if captured_count > 0:
        pdf_path = output_dir / config.get("output_filename", "book.pdf")
        result = create_pdf(screenshots_dir, pdf_path, start_page, start_page + captured_count - 1)
        if result:
            size_mb = pdf_path.stat().st_size / 1024 / 1024
            print(f"\nPDF保存完了: {pdf_path}")
            print(f"ファイルサイズ: {size_mb:.1f} MB")
    
    # スクリーンショット削除
    if config.get("delete_screenshots", False):
        print("\nスクリーンショットを削除中...")
        for f in screenshots_dir.glob("*.png"):
            f.unlink()
    
    print("\n完了！")


if __name__ == "__main__":
    main()
