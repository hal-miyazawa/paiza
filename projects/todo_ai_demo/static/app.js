// このファイルは JSX を使って最小のUIを定義します。
// 目的は「AI相談 → タイトル/メモに反映」の流れを理解すること。
// 余計な機能（DB保存など）は入れていません。

const { useState } = React;

function App() {
  // フォーム状態
  // あとで変わる値 = state（useState）
  const [title, setTitle] = useState("");
  const [memo, setMemo] = useState("");

  // モーダル状態
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [aiText, setAiText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // AI相談を送信
  const sendToAI = async () => {
    setIsLoading(true);
    setError("");

    try {
      const res = await fetch("/api/propose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: aiText }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "エラーが発生しました");
      }

      // 返ってきた内容をフォームに反映
      setTitle(data.title || "");
      setMemo(data.memo || "");

      // モーダルを閉じる
      setIsModalOpen(false);
      setAiText("");
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setIsLoading(false);
    }
  };

  // フォームのリセット
  const resetForm = () => {
    setTitle("");
    setMemo("");
  };

  return (
    <div className="container">
      <div className="header">
        <h1>TODO AI デモ</h1>
        <button className="button" onClick={() => setIsModalOpen(true)}>
          AIに相談
        </button>
      </div>

      <div className="card">
        <label className="label">タイトル</label>
        <input
          className="input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="例: 芋掘り作業の計画"
        />

        <div style={{ height: 12 }} />

        <label className="label">メモ</label>
        <textarea
          className="textarea"
          value={memo}
          onChange={(e) => setMemo(e.target.value)}
          placeholder="補足メモを入力"
        />

        <div className="row">
          <button className="button secondary" onClick={resetForm}>
            リセット
          </button>
          <button className="button" disabled>
            保存（未実装）
          </button>
        </div>
      </div>

      {isModalOpen && (
        <div className="modal-backdrop" onClick={() => setIsModalOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>AIに相談</h2>
            <p className="label">相談内容</p>
            <textarea
              className="textarea"
              value={aiText}
              onChange={(e) => setAiText(e.target.value)}
              placeholder="例: いもをほりたい"
            />

            <div className="row">
              <button
                className="button secondary"
                onClick={() => setIsModalOpen(false)}
                disabled={isLoading}
              >
                キャンセル
              </button>
              <button
                className="button"
                onClick={sendToAI}
                disabled={isLoading || !aiText.trim()}
              >
                送信
              </button>
            </div>

            {isLoading && <div className="loading">考え中...</div>}
            {error && <div className="error">{error}</div>}
          </div>
        </div>
      )}
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
