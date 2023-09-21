import os
import schedule
import time
import shutil
import glob

def deleteOldFiles():
    try:
        # 削除対象となる経過時間（分）
        elapsed_time = 3

        # zipファイルを削除
        try:
            # ワイルドカードに一致するファイルを取得
            zip_files = glob.glob("*_images.zip")

            # ファイルを削除
            for zip_file in zip_files:
                os.remove(zip_file)

        except Exception as e:
            print(f"Error: {e}")

        # imgs内のファイルを取得
        img_dir = "static/imgs/"
        user_ids = os.listdir(img_dir)
        for user_id in user_ids:
            books = os.listdir(os.path.join(img_dir, user_id))
            for book in books:
                if book=="__MACOSX":
                    shutil.rmtree(os.path.join(img_dir, user_id, "__MACOSX"))
                files = os.listdir(os.path.join(img_dir, user_id, book))
                # 現在時刻を取得
                current_time = time.time()

                # ファイルを1つずつチェック
                for file in files:
                    # ファイルの更新日時を取得
                    mtime = os.path.getmtime(os.path.join(img_dir, user_id, book, file))
                    # 経過時間を計算
                    diff_time = current_time - mtime
                    # 経過時間がelapsed_time分を超えている場合、ファイルを削除
                    if diff_time >= elapsed_time * 60:
                        os.remove(os.path.join(img_dir, user_id, book, file))
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