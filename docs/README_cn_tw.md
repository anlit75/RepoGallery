<p align="center">
   <img width="100%" src="img/RepoGallery-banner-dark.png" alt="RepoGallery Logo" />
   <h1 align="center">RepoGallery</h1>
   <h3 align="center">三個檔案，馬上開始！</h3>
   <p align="center">為你所有的 GitHub 專案打造的精美展示頁。:art:</p>
</p>

<br>

<p align="center"> <a href="https://anlit75.github.io/RepoGallery">觀看線上範例</a>  |  <a href="https://anson-cheng.github.io/RepoGallery-demo-dark">更多範例</a></p>

<br>

<p align="center"> <a href="../README.md">English</a>  |  <a href="README_cn_tw.md">繁體中文</a></p>

<br>

<h2 align="center">✨ 主要特色 ✨</h2>

<p align="center">
  🔹 安裝簡單 • ⚡ 自動部署 <br>
  🎨 高度自訂 • 💎 現代化設計 <br>
  🔄 升級不會有合併衝突 • 🚀 提供線上範例
</p>

<br>

## :gear: 事前準備

一個 **GitHub 帳號**，以及一個用來發佈頁面的 repository。全新的空 repository 就可以，
**不需要 fork 任何東西**。

## :rocket: 快速開始

### 步驟 1. **複製起始檔案**

把 [`examples/starter/`](../examples/starter) 裡的三個檔案複製到你自己的 repository：

```
.github/workflows/gallery.yml   ← 幫你執行 RepoGallery
config.yaml                     ← 你的設定
assets/custom_image.yaml        ← 選用，指定專案圖片
```

安裝就這樣而已。產生器本身留在上游 repository，透過 `anlit75/RepoGallery@v2` 這個 action 執行，
所以你的 repository 裡永遠不會有一份引擎程式碼的複本。

### 步驟 2. **GitHub 設定**

> [!IMPORTANT]\
> 這些設定**必須**透過 GitHub 網頁版操作（GitHub Mobile 不支援）。

#### **A. 設定 GitHub Pages**
<details>
<summary>前往 <strong>Settings > Pages</strong></summary>
   <img width="100%" style="padding: 10px;" src="img/pages.png" alt=""/>
</details>

<details>
<summary>✅ 將 <code>Build and deployment</code> 的 <strong>Source</strong> 設為 <strong>GitHub Actions</strong></summary>
   <img width="100%" style="padding: 10px;" src="img/build_and_deployment.png" alt=""/>
</details>

#### **B. 啟用 GitHub Actions**
<details>
<summary>前往 <strong>Settings > Actions > General</strong></summary>
   <img width="100%" style="padding: 10px;" src="img/actions_general.png" alt=""/>
</details>

<details>
<summary>✅ 將 <code>Action permissions</code> 設為 <strong>Allow all actions and reusable workflows</strong></summary>
   <img width="100%" style="padding: 10px;" src="img/actions_permissions.png" alt=""/>
</details>

### 步驟 3. **執行**

前往 **Actions** <img src="img/actions.png" style="height: 20px !important;width: 20px !important;" > 分頁，
選擇 **RepoGallery**，點擊 **Run workflow**。

> [!NOTE]\
> 它也會在**每天 UTC 00:00** 自動執行 🕛，以及**每次 push 到 `main`** 時執行。

### 步驟 4. **個人化設定（選用）**

:art: 編輯 `config.yaml` 來自訂你的展示頁：標題、佈景主題、要顯示哪些 repo、排序方式等等。
所有選項都寫在 [**config.yaml**](../config.yaml) 的註解裡。

commit 並 push，這個 push 就會重新部署頁面。

### 步驟 5. **打開你的 RepoGallery 頁面**

📌 `https://<你的-github-使用者名稱>.github.io/<你的-repo-名稱>`

## 🔄 如何升級

不用同步，也不會有合併衝突。

你的 workflow pin 在 `anlit75/RepoGallery@v2`。`v2` 這個 tag 永遠指向最新的 `2.x` 版本，
所以**修好的 bug 和新功能會在下一次排程執行時自動送達**，你什麼都不用做。

當有破壞性變更的 `v3` 發佈時，release notes 會說明改了什麼；升級只要改一行：

```diff
-      - uses: anlit75/RepoGallery@v2
+      - uses: anlit75/RepoGallery@v3
```

如果想鎖定特定版本，可以直接寫完整的 tag，例如 `anlit75/RepoGallery@v2.0.0`。

### 從 fork 版本遷移（v1.2.0 以前）

舊版本是用 fork 的方式安裝的。遷移方式：

1. 在你的 fork 裡，刪掉 `config.yaml` 和 `assets/custom_image.yaml` **以外**的所有檔案。
2. 把 `examples/starter/.github/workflows/gallery.yml` 複製進去。
3. 從你的 `config.yaml` 移除 `site.version` 這個欄位，它已經不存在了。
4. commit 並 push。

你的 Pages 網址和設定都會保留。

## ⚙️ Action 參數

| 參數 | 預設值 | 說明 |
|---|---|---|
| `username` | repository 擁有者 | 要顯示哪個 GitHub 使用者的 repo |
| `token` | `github.token` | 呼叫 GitHub API 用的 token |
| `config` | `config.yaml` | 設定檔路徑 |
| `output` | `public` | 產生的網站寫到哪個目錄 |
| `assets` | `assets` | 你自己的檔案，會一起發佈到網站 |
| `python-version` | `3.11` | 執行產生器的 Python 版本 |

## 🛠 運作原理（給好奇的人）

`action.yml` 會執行 `scripts/generate_html.py`，它會：

1. 讀取你 repository 裡的 `config.yaml`
2. 透過 GitHub API 取得你的 repositories
3. 把 `templates/v1/` 渲染成 `public/`

接著你的 workflow 把 `public/` 交給 `actions/deploy-pages`。

### 想了解更多？
可以看看 `scripts/`、`templates/` 和 `tests/` 這幾個資料夾。

依賴宣告在 `pyproject.toml`，用 [uv](https://docs.astral.sh/uv/) 鎖定版本。本機跑測試：

```bash
uv run --dev pytest
```

`requirements.txt` 是從 `uv.lock` 產生的（`uv export --no-dev --no-emit-project`），
action 安裝的就是它；改動依賴後記得重新產生。

## ☕ 請我喝杯咖啡
喜歡這個專案嗎？請我喝杯咖啡，讓我有動力繼續改進它！<br>
在 Buy Me a Coffee 上支持我 :sparkling_heart:

<a href="https://www.buymeacoffee.com/anlit" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 150px !important;" ></a>

## 📄 授權

本專案採用 [Apache License 2.0](../LICENSE) 授權。
