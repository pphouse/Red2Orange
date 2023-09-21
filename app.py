import cv2
import datetime
from zipfile import ZipFile
import shutil
import numpy as np
import hashlib
import os
import subprocess
from flask import Flask, render_template, request, send_file, redirect, url_for, session, jsonify
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
def Red2Orange():
    img_dir = "static/imgs/"
    img_path = None
    global progress
    progress = 0

    if request.method == 'POST':
        try:
            button_value = request.form.get('button')
            print("button_value:", button_value)
            # ボタン1(ファイル用)が押された時の処理
            if button_value == "button1":
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

                    # ユーザーIDのディレクトリ下に画像を保存
                    dt_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                    # 文字化け対策
                    img_path = os.path.join(img_dir, hashed_user_id, dt_now + "_medu4_" + request.files["img"].filename[-7:])
                    os.mkdir(os.path.join(img_dir, hashed_user_id))
                    cv2.imwrite(img_path, img)


                    #change colorファイル実行
                    inputCommand = [f"python change_color.py {img_path}"]
                    subprocess.run(inputCommand, shell=True)
                    print("change color!!")


                    # セッションにハッシュ化したユーザーIDを保存
                    session['user_id'] = hashed_user_id

                    # POST処理の後、GETリクエストをトリガー
                    return redirect(url_for('download_image'))

                else:
                    # 画像が格納されていなければ、Noneを設定する
                    img_path = None

            # ボタン２(zipファイル用)が押された時の処理
            elif button_value == "button2":
                # ユーザーIDを生成
                user_id = str(uuid.uuid4())
                # SHA-256ハッシュを計算
                hashed_user_id = hashlib.sha256(user_id.encode()).hexdigest()
                # 短縮
                hashed_user_id = hashed_user_id[:10]

                #時刻取得
                dt_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

                # POSTにより受信したZIPファイルを保存
                zip_file = request.files['folder']
                zip_path = os.path.join(img_dir, hashed_user_id,  "uploaded_folder.zip")
                os.mkdir(img_dir)
                print("hashed_user_idのディレクトリ作ります!")
                os.mkdir(os.path.join(img_dir, hashed_user_id))
                zip_file.save(zip_path)
                print("zip file 保存しました")

                # ZIPファイルを解凍
                unzip_path = os.path.join(img_dir, hashed_user_id)
                shutil.unpack_archive(zip_path, unzip_path)
                print("zip file 解凍しました")
                
                # 展開
                book_path = os.path.join(unzip_path, zip_file.filename.split(".zip")[0])
                print("book_path:", book_path)
                
                for i, path in enumerate(os.listdir(book_path)):
                    # 進捗バー
                    progress = int(100*i/len(os.listdir(book_path)))+1
                    print("progress:", progress)
                    
                    if path.endswith(".jpg"):
                        #ファイル名の先頭に時刻を追加する
                        dt_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                        #文字化け対策
                        new_path = os.path.join(book_path, dt_now + "_medu4_" + path[-7:])
                        os.rename(os.path.join(book_path, path), new_path)
                        #change colorファイル実行
                        inputCommand = [f"python change_color.py {new_path}"]
                        subprocess.run(inputCommand, shell=True)

                # セッションにハッシュ化したユーザーIDを保存
                session['user_id'] = hashed_user_id

                # POST処理の後、GETリクエストをトリガー
                return redirect(url_for('download_zip'))


            else:
                print("エラー発生")
        except Exception as e:
            # エラー処理
            print('エラー発生')
            print(e)
            img_path = None

    return render_template("index.html", img_path=img_path, progress=progress)

@app.route('/download_image')
def download_image():
    # セッションからハッシュ化したユーザーIDを取得
    hashed_user_id = session.get('user_id')


    # ユーザーIDに対応する処理実行後の画像をダウンロード
    img_dir = "static/imgs/"
    img_files = os.listdir(os.path.join(img_dir, hashed_user_id))
    for img_file in img_files:
        return send_file(os.path.join(img_dir, hashed_user_id, img_file), as_attachment=True, download_name="_".join(img_file.split("_")[1:]))

    # ユーザーIDがない場合や処理実行後の画像が見つからない場合はエラーメッセージを表示
    return "ダウンロードする画像がありません"

@app.route('/download_zip')
def download_zip():
    # セッションからハッシュ化したユーザーIDを取得
    hashed_user_id = session.get('user_id')
    
    img_dir = "static/imgs/"

    #uploaded_folder.zipを削除
    # os.remove(os.path.join(img_dir, hashed_user_id, "uploaded_folder.zip"))
    #現在時刻取得
    dt_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")

    # ユーザーID/book ディレクトリ下の画像をzipファイルに圧縮
    books = os.listdir(os.path.join(img_dir, hashed_user_id))
    for book in books:
        #__MACOSXフォルダとダウンロード済みのフォルダは無視
        if book != "__MACOSX" and not "downloaded" in book and not ".zip" in book:
            # ファイル名から時刻を削除
            print("download_zip!!")
            source_dir = os.path.join(img_dir, hashed_user_id, book)
            for file in os.listdir(source_dir):
                new_file = file.split("_")[1] + "_" + file.split("_")[2]
                os.rename(os.path.join(source_dir, file), os.path.join(source_dir, new_file))
            zip_file = f"{dt_now}_images.zip"
            shutil.make_archive("temp_directory", "zip", source_dir)
            shutil.move("temp_directory.zip", zip_file)
            
            #ダウンロードするフォルダの名前にdownloadedを追加
            os.rename(source_dir, os.path.join(img_dir, hashed_user_id, "downloaded_"+book))
            #zipファイルをダウンロード
            return send_file(zip_file, as_attachment=True, mimetype="application/zip", download_name=f"{dt_now}_images.zip")
        
@app.route('/get_progress')
def get_progress():
    try:
        # 仮の進捗情報を生成する（実際には進捗計算ロジックをここに追加）
        global progress # 0から100の範囲の進捗

        # 進捗情報をJSON形式でクライアントに返す
        return jsonify(progress=progress)
    except:
        print("progressが定義されていないがスルーして良い")
        return None

if __name__ == "__main__":
    app.run(debug=True)
