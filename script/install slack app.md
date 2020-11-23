# 前準備
```
curl -sL https://rpm.nodesource.com/setup_8.x | sudo bash -
yum install nodejs npm -y
npm install -g n
yum remove nodejs npm
```

# Boltプロジェクトの設定
```
mkdir slack
cd slack
npm init
```

```
vim index.js
```
```
const { App } = require('@slack/bolt');

// Initializes your app with your bot token and signing secret
const app = new App({
token: process.env.SLACK_BOT_TOKEN,
signingSecret: process.env.SLACK_SIGNING_SECRET
});

app.message('hello', async ({ message, say }) => {
  // say() sends a message to the channel where the event was triggered
  await say(`Hey there <@${message.user}>!`);
});

(async () => {
// Start your app
await app.start(process.env.PORT || 3000);

console.log('⚡️ Bolt app is running!');
})();
```
sign in
・https://api.slack.com/apps/A01C9BC95LZ/general?
OAuthのbot id
・https://api.slack.com/apps/A01C9BC95LZ/oauth?
```
export SLACK_SIGNING_SECRET=xxxx
export SLACK_BOT_TOKEN=xxxxxxxx
```

# slackの管理コンソール
Event Subscriptions

# port 解放
firewall-cmd --add-port=3000/tcp --zone=public --permanent