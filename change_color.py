import os
import sys
import cv2


#画像が入っているディレクトリのパス
img_path = sys.argv[1]

def detect_rectangle_and_change_color(img_path, height):
    # 画像を読み込む
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 長方形を検出する
    ret, thresh = cv2.threshold(gray, 200, 255, 0)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 100 and h > height - 10 and h < height + 10:  # 長方形のサイズをチェック
            roi = img[y:y+h, x:x+w]
            # 赤色の文字を薄いオレンジ色(#FFCE86)に変更 
            mask = (roi[:, :, 2] >= 1.25 * roi[:, :, 1]) & (roi[:, :, 2] >= 1.25 * roi[:, :, 0]) 
            # roi[mask] = [134, 206, 255]
            roi[mask] = [182, 241, 255]  #FFF1B6

    print(f"長方形は{len(contours)}個")
    print(f"サイズ {img.shape}")

    # 画像を保存
    cv2.imwrite(img_path, img)

# 実行
detect_rectangle_and_change_color(img_path, 80)
