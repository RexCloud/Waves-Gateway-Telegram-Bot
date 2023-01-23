# Waves Gateway Telegram Bot
Waves Gateway monitoring &amp; funds withdrawal Telegram bot for Waves

## Installing
You can install by cloning repo and installing required packages
```
$ git clone https://github.com/RexCloud/Waves-Gateway-Telegram-Bot
$ cd Waves-Gateway-Telegram-Bot
$ pip install -r requirements.txt
```

## Setup
Configure environment variables:

`bot_token` — Telegram bot API token

`refresh_token` — WX.Network (Waves Exchange) refresh token

`receiver_address` — EVM address for receiving payments from subscription buyers

`seed` — Used for funds withdrawal (Optional, enter random text)

## Usage
Run waves_telegram.py to start the bot

`python waves_telegram.py`

### Admin commands:
`/add_user @username/username` — Manually add user and give lifetime subscription

`/remove_user @username/username` — Manually remove user and his subscription

`/get_users` — Retrieve all users, their notification mode (0 - off, 1 - standard, 2 - silent) and subscription expiration timestamp (0 - no expiration)

`/try_withdraw token amount` — Start trying to withdraw token (USDC/USDT/BUSD) to `receiver_address`, e.g. `/try withdraw USDT 1234.56`

`/stop_try_withdraw` — Stop trying to withdraw
