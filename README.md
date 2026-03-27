# 🎰 Gacha App

イベント向けのガチャWebアプリです。  
実際のイベントで運用し、その場でガチャを回して当選者を即時表示する体験を実現しました。

---

## 🔗 リンク

| | URL |
|---|---|
| デモ | https://laf-gacha.vercel.app/demo/ |
| 本番 | https://laf-gacha.vercel.app |

> ※ デモURLでは在庫の変動・当選履歴の保存は行われません。自由にお試しください。

---

## 📱 主な機能

- **ガチャを回す**：ボタン1つでその場で抽選・結果を即時表示
- **当選履歴の表示**：過去の当選者をリアルタイムで一覧表示
- **在庫管理**：景品ごとの残数をリアルタイムで管理・自動減算
- **管理者画面**：景品の設定・在庫数の変更をGUI上で操作可能

---

## 🛠 使用技術

| 分類 | 技術 |
|---|---|
| フロントエンド | Next.js / React |
| データベース（当選履歴） | Firebase Firestore |
| データベース（在庫・設定） | Google スプレッドシート |
| ホスティング | Vercel |

---

## 💡 工夫した点

- **2種類のDBを用途で使い分け**：リアルタイム性が必要な当選履歴はFirebase、管理のしやすさを優先する在庫・設定はGoogleスプレッドシートで管理
- **管理者画面を実装**し、非エンジニアでも景品設定や在庫変更ができるUIを設計
- ポートフォリオ公開用に `/demo/` URLではDBへの書き込みをスキップするデモモードを実装

---

## 📸 スクリーンショット

<!-- スクリーンショットをここに追加 -->
![トップ画面](https://github.com/user-attachments/assets/77993386-8894-4203-8723-ade1a4ed0323)
![ガチャ結果画面](https://github.com/user-attachments/assets/1184f5e5-f848-4df5-97e3-2f06d7b37d84)

---

## ⚙️ ローカル起動方法

```bash
git clone https://github.com/noah-nozomu/gacha-app
cd gacha-app
npm install

# .env.localファイルを作成してFirebase・スプレッドシートの設定を記入
npm run dev
```
