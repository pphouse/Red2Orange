var fileArea = document.getElementById('dragDropArea');
var fileInput = document.getElementById('fileInput');

// dragover時の処理
fileArea.addEventListener('dragover', function(evt){
    evt.preventDefault();
    fileArea.classList.add('dragover');
});

// dragleave時の処理
fileArea.addEventListener('dragleave', function(evt){
    evt.preventDefault();
    fileArea.classList.remove('dragover');
});

// drop時の処理
fileArea.addEventListener('drop', function(evt){
    evt.preventDefault();
    fileArea.classList.remove('dragenter');
    var files = evt.dataTransfer.files;

    // fileCheck関数によりファイルチェック
    if (fileCheck(files[0])) { 
        console.log("DRAG & DROP");
        fileInput.files = files;
        // photoPreview関数呼び出し
        photoPreview('onChenge',files[0]);
    }
});


function photoPreview(event, f = null) {
    var file = f;
    // fileがnullであれば、eventより取得
    if(file === null){
        file = event.target.files[0];
    }

    // 変数定義
    var reader = new FileReader();
    var preview = document.getElementById("previewArea");
    var previewImage = document.getElementById("previewImage");

    // プレビューエリアの画像が既に存在すれば削除する
    if(previewImage != null) {
        preview.removeChild(previewImage);
    }

    // 画像ファイルをプレビューエリアに追加
    reader.onload = function(event) {
        var img = document.createElement("img");
        img.setAttribute("src", reader.result);
        img.setAttribute("id", "previewImage");
        preview.appendChild(img);
    };

    // 送信用に画像ファイルの読み込み
    reader.readAsDataURL(file);

    // ドラッグ&ドロップエリアのテキスト非表示
    document.getElementById("drag-drop-comment").style.display ="none";
}


// 許容するファイル拡張子
const allowExtensions = '.(jpeg|jpg|png|webp)$';

// ファイルチェック処理
function fileCheck(file) {
    if (!file.name.match(allowExtensions)) {
        alert('拡張子が jpeg, jpg, png, webp 以外のファイルはアップロードできません。');
        return false;
    }
    return true;
}