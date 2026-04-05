# hello-blender-three-live-preview

Blender で作業中のモデルを GLB に書き出し、three.js + Vite で即確認するための検証用リポジトリです。  
現在は「保存時の自動実行」ではなく、Blender 上のボタンから明示的に書き出す構成にしています。

## できること

- Blender の `ExportTarget` コレクションを `scene.glb` として書き出す
- three.js 側で `/models/scene.glb` を読み込み表示する
- Vite 開発サーバー上で更新をすぐ確認する

## 前提環境

- Node.js 20 以上（Vite 8 系）
- Blender 4.x（Python スクリプト実行）

## セットアップ

```bash
npm install
```

## Web 側の起動

```bash
npm run dev
```

起動後、表示 URL（通常 `http://localhost:5173`）をブラウザで開きます。

## Blender 側の書き出し手順

1. `blender/hello_auto_export_gltf.blend` を開く
2. `blender/scripts/auto_export_gltf.py` を Blender の Text Editor で開く
3. `Run Script` を実行する
4. 3D View のサイドバー (`N`) の `Tool` タブにある `Auto GLB Export` パネルから `Export Auto GLB` を押す

この操作で、`public/models/scene.glb` が更新されます。

## 重要な前提

- `.blend` を一度保存してから実行してください（未保存だとエラーになります）
- 書き出し対象は `ExportTarget` という名前のコレクションです
- 出力先は固定で `public/models/scene.glb` です

## トラブルシュート

- `Collection "ExportTarget" was not found`  
  `ExportTarget` コレクション名を確認してください。
- 画面にモデルが出ない  
  ブラウザの開発者コンソールで `/models/scene.glb` 読み込みエラーを確認してください。

## 発表資料

ライトニングトーク用の資料は `talk/` にあります。  
詳細は `talk/README.md` を参照してください。
