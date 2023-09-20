import cv2
import datetime
import numpy as np
import hashlib
import os
import subprocess
from flask import Flask, render_template, request, send_file, redirect, url_for, session
from flask_session import Session
import uuid  # ユーザーIDを生成するために使用

app = Flask(__name__)

# セッションをセットアップ
app.config['SESSION_TYPE'] = 'filesystem'  # セッションデータをファイルに保存
app.config['SESSION_PERMANENT'] = False  # セッションの有効期限を設定しない
Session(app)

# 古いファイル削除処理の呼び出し
command = ["python", "deleteOldFiles.py"]
proc = subprocess.Popen(command)

def download_image(image_path):
    # 画像をダウンロード
    return send_file(image_path, as_attachment=True)

@app.route('/', methods=["GET", "POST"])
def sizeUp():
    img_dir = "static/imgs/"
    img_path = None

    if request.method == 'POST':
        try:
            # POSTにより受信した画像を読み込む
            stream = request.files['img'].stream
            img_array = np.asarray(bytearray(stream.read()), dtype=np.uint8)

            # 画像が格納されていれば、後段の処理に進む
            if not len(img_array) == 0:
                img = cv2.imdecode(img_array, 1)

                # ユーザーIDを生成
                user_id = str(uuid.uuid4())

                # SHA-256ハッシュを計算
                hashed_user_id = hashlib.sha256(user_id.encode()).hexdigest()
                # 短縮
                hashed_user_id = hashed_user_id[:10]

                # ファイル名にユーザーIDを含めて保存
                dt_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                img_path = os.path.join(img_dir, hashed_user_id + "_" + dt_now + ".jpg")
                out_path = os.path.join(img_dir, hashed_user_id + "_" + dt_now + "_sizeup" + ".jpg")

                cv2.imwrite(img_path, img)

                # Real-ESRGAN処理実行
                os.chdir('realesrgan/')
                inputCommand = ['./realesrgan-ncnn-vulkan','-i', "../" + img_path,'-o', "../" + out_path]
                subprocess.run(inputCommand)
                print("realesrgan!!")
                os.chdir('../')

                # セッションにハッシュ化したユーザーIDを保存
                session['user_id'] = hashed_user_id

                # POST処理の後、GETリクエストをトリガー
                return redirect(url_for('download_image'))

            else:
                # 画像が格納されていなければ、Noneを設定する
                img_path = None
        except Exception as e:
            # エラー処理
            print('エラー発生')
            print(e)
            img_path = None

    return render_template("index.html", img_path=img_path)

@app.route('/download_image')
def download_image():
    # セッションからハッシュ化したユーザーIDを取得
    hashed_user_id = session.get('user_id')

    if hashed_user_id:
        # ユーザーIDに対応する処理実行後の画像を探してダウンロード
        img_dir = "static/imgs/"
        img_files = os.listdir(img_dir)
        for img_file in img_files:
            if img_file.startswith(hashed_user_id) and img_file.endswith("_sizeup.jpg"):
                img_path = os.path.join(img_dir, img_file)
                return send_file(img_path, as_attachment=True)

    # ユーザーIDがない場合や処理実行後の画像が見つからない場合はエラーメッセージを表示
    return "ダウンロードする画像がありません"

if __name__ == "__main__":
    app.run(debug=True)
