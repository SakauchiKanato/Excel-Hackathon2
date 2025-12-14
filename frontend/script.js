async function startAnalysis() {
    const fileInput = document.getElementById('fileInput');
    const statusDiv = document.getElementById('statusMessage');
    const btn = document.getElementById('uploadBtn');

    if (fileInput.files.length === 0) {
        alert("画像ファイルを選択してください！");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    // ロード中のUI更新
    btn.disabled = true;
    btn.textContent = "分析中...";
    statusDiv.textContent = "⏳ AIが画像を解析しています... (約15秒)";
    statusDiv.style.color = "#2980b9";

    try {
        // サーバーに送信（相対パス '/analyze' を指定）
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error("サーバーエラーが発生しました");
        }

        // Excelファイル(Blob)の取得とダウンロード発火
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        // ファイル名の取得試行
        let fileName = "分析結果.xlsx";
        const disposition = response.headers.get('Content-Disposition');
        if (disposition && disposition.indexOf('filename=') !== -1) {
             // 簡易的なファイル名抽出
             const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
             if (matches != null && matches[1]) { 
                 fileName = matches[1].replace(/['"]/g, '');
             }
        }

        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        statusDiv.textContent = "✅ 分析完了！ダウンロードされました。";
        statusDiv.style.color = "#27ae60";

    } catch (error) {
        console.error(error);
        statusDiv.textContent = "❌ エラー: " + error.message;
        statusDiv.style.color = "#c0392b";
    } finally {
        btn.disabled = false;
        btn.textContent = "分析スタート";
    }
}