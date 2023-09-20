import os
import schedule
import time

def deleteOldFiles():
    try:
        # 削除対象となる経過時間（分）
        elapsed_time = 3

        # imgs内のファイルを取得
        img_dir = "static/imgs/"
        files = os.listdir(img_dir)
        # 現在時刻を取得
        current_time = time.time()

        # ファイルを1つずつチェック
        for file in files:
            # ファイルの更新日時を取得
            mtime = os.path.getmtime(img_dir + file)
            # 経過時間を計算
            diff_time = current_time - mtime
            # 経過時間がelapsed_time分を超えている場合、ファイルを削除
            if diff_time >= elapsed_time * 60:
                os.remove(img_dir + file)
                print('oldファイル削除: ' + file)
                
    except Exception as e:
        # エラー処理
        print('oldファイル削除処理でエラー発生')
        print(e)

# 1分おきにファイル削除処理を呼び出す
schedule.every(1).minutes.do(deleteOldFiles)

# スケジュール処理の設定
while True:
    schedule.run_pending()
    time.sleep(1)