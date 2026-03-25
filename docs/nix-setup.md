# 10_nix-setup

作成日時: 2026年3月25日
最終更新者: KOU050223

# Nix 開発環境セットアップガイド

このプロジェクトでは Nix Flakes と direnv を使用して、統一された開発環境を提供しています。

---

## 0️⃣ 前提条件

| 項目 | 内容 |
| --- | --- |
| 対応OS | macOS, Linux |
| 所要時間 | 初回セットアップ: 約10-15分 |
| ディスク容量 | 約2-3GB（Nix store） |

---

## 1️⃣ Nix のインストール

### macOS / Linux 共通

```bash
# Determinate Systems インストーラー（推奨）
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
```

または公式インストーラー:

```bash
sh <(curl -L https://nixos.org/nix/install) --daemon
```

インストール後、新しいターミナルを開くか、以下を実行:

```bash
. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh
```

### 確認

```bash
nix --version
# nix (Nix) 2.x.x
```

---

## 2️⃣ Flakes の有効化

Determinate Systems インストーラーを使用した場合、Flakes は自動的に有効化されています。

公式インストーラーを使用した場合は、以下を設定:

```bash
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
```

---

## 3️⃣ direnv のインストール

### macOS (Homebrew)

```bash
brew install direnv
```

### Linux (apt)

```bash
sudo apt install direnv
```

### シェル設定

使用しているシェルに応じて設定を追加:

**Bash** (`~/.bashrc`):
```bash
eval "$(direnv hook bash)"
```

**Zsh** (`~/.zshrc`):
```zsh
eval "$(direnv hook zsh)"
```

**Fish** (`~/.config/fish/config.fish`):
```fish
direnv hook fish | source
```

設定後、シェルを再起動:

```bash
exec $SHELL
```

---

## 4️⃣ nix-direnv のインストール（推奨）

nix-direnv を使用すると、環境のキャッシュが効いて切り替えが高速になります。

```bash
# Homebrewの場合
brew install nix-direnv

# または Nix 経由
nix profile install nixpkgs#nix-direnv
```

direnv の設定に追加 (`~/.config/direnv/direnvrc`):

```bash
source $HOME/.nix-profile/share/nix-direnv/direnvrc
# または Homebrew の場合
source $(brew --prefix nix-direnv)/share/nix-direnv/direnvrc
```

---

## 5️⃣ プロジェクトでの使用

### 初回セットアップ

```bash
cd /path/to/Jyogi_navi

# direnv を許可
direnv allow
```

初回は依存パッケージのダウンロードに数分かかります。

### 動作確認

```bash
# 自動的に開発環境がロードされる
cd /path/to/Jyogi_navi

# ツールのバージョン確認
node --version    # v20.x.x
pnpm --version    # 9.x.x
python --version  # Python 3.13.x
uv --version
gh --version
```

### 手動でシェルに入る場合

```bash
nix develop
```

---

## 6️⃣ トラブルシューティング

### direnv: error .envrc is blocked

```bash
direnv allow
```

### Flakes が有効になっていない

```bash
# nix.conf を確認
cat ~/.config/nix/nix.conf

# experimental-features = nix-command flakes が含まれていることを確認
```

### 環境が古い場合

```bash
# flake.lock を更新
nix flake update

# 環境を再読み込み
direnv reload
```

### キャッシュをクリア

```bash
# direnv キャッシュを削除
rm -rf .direnv/

# 再読み込み
direnv allow
```

---

## 7️⃣ よくある質問

### Q: Nix を使わずに開発できますか？

A: はい。従来通り手動で Node.js、Python、pnpm、uv などをインストールしても開発できます。ただし、バージョンの一致は各自で管理する必要があります。

### Q: CI/CD でも Nix を使いますか？

A: 現時点では GitHub Actions で直接ツールをインストールしています。将来的に Nix に統一する可能性があります。

### Q: ディスク容量が心配です

A: Nix store は `~/.nix` または `/nix/store` に保存されます。不要なパッケージは以下で削除できます:

```bash
nix-collect-garbage -d
```

---

## 8️⃣ 参考リンク

- [Nix 公式ドキュメント](https://nixos.org/manual/nix/stable/)
- [Nix Flakes](https://nixos.wiki/wiki/Flakes)
- [direnv](https://direnv.net/)
- [nix-direnv](https://github.com/nix-community/nix-direnv)
- [Determinate Systems Nix Installer](https://github.com/DeterminateSystems/nix-installer)
