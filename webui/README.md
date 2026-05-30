# 情书 Agent

一个以“给阿嬷的情书”为灵感的前端 GUI 原型。

## 预览

在项目目录运行：

```powershell
python -m http.server 4173
```

然后打开：

- `http://127.0.0.1:4173/`

也可以看几个演示状态：

- `http://127.0.0.1:4173/?demo=compose`
- `http://127.0.0.1:4173/?demo=answer`
- `http://127.0.0.1:4173/?demo=history`

## 后续接入 Agent

真实对话接口预留在 [app.js](C:/Users/HP/OneDrive/Desktop/agentui/app.js:282) 的 `window.agentConnector.ask`：

```js
window.agentConnector = {
  ask: async ({ question, history }) => {
    return "这里返回真实 agent 的回答";
  },
};
```

## 素材

- 信纸背景：`assets/letter-paper.png`
- 木槿花：`assets/hibiscus.png`
- 纸飞机：`assets/paper-plane.png`
