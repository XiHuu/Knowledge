# DeepSeek API 账户余额与用量查询

DeepSeek 开放平台除了聊天补全，还提供**账户余额**接口 —— 用自己的 API key 就能查，
不必登录控制台。

> ⚠️ 余额是**账户私有数据**。本文只记录**查询方法**，任何具体金额都不应写进公开仓库、
> 提交历史或日志。

## 余额接口

```bash
curl -s https://api.deepseek.com/user/balance \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Accept: application/json"
```

返回：

```json
{
  "is_available": true,
  "balance_infos": [
    {
      "currency": "CNY",
      "total_balance": "135.84",
      "granted_balance": "121.22",
      "topped_up_balance": "14.62"
    }
  ]
}
```

| 字段 | 含义 |
| --- | --- |
| `is_available` | 账户当前是否可用于调用（余额耗尽会变 `false`） |
| `currency` | 币种，人民币账户 `CNY`、美元账户 `USD` |
| `total_balance` | 总可用余额 = 赠金 + 充值 |
| `topped_up_balance` | **充值余额**（自己充的，一般不过期） |
| `granted_balance` | **赠金**（平台赠送，通常有有效期，先于充值余额消耗） |

**`balance_infos` 是数组**：同一账户可能持有多种币种，取值时别写死 `[0]` 的币种，
要按 `currency` 匹配。

## 坑

- **这是只读接口**，不会产生任何费用，可以随便查。
- 认证方式与模型调用一致：`Authorization: Bearer <API_KEY>`。
- **key 错误/失效返回 401，不是"余额为 0"** —— 别把 401 误读成没钱了。
  两者要分开判断：先看 HTTP 状态码，再看 `is_available`。
- 余额不足时模型调用会被拒（DeepSeek 对余额不足返回 `402 Insufficient Balance`），
  而不是静默降级。

## 在 Hermes 里查

Hermes 侧 `providers.deepseek.key_env` 指向 `DEEPSEEK_API_KEY`，实际值存在
`~/.hermes/.env`。读出后直接打接口即可 —— **注意别把 key 打印到终端、日志或聊天里**：

```bash
KEY=$(grep -E '^DEEPSEEK_API_KEY=' ~/.hermes/.env | cut -d= -f2- | tr -d '"'"'"' ')
curl -s https://api.deepseek.com/user/balance -H "Authorization: Bearer $KEY"
```

自查脚本里建议只回显 `key` 的**长度与前缀**（如 `长度 35，前缀 sk-9a1****`），
用来确认"取到的是不是 key"，同时不泄露明文。
