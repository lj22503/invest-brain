# InvestBrain SEO 技术修复速查表（Next.js 14 App Router）

> 所有代码直接可复制到 InvestBrain 项目。部署平台应为 Vercel（与现有一致）。
> 修复优先级：**P0 = sitemap + GSC 注册 + meta description**；**P1 = OG + canonical + JSON-LD**。

---

## 1. 生成 sitemap.xml（修复 P0：当前 404）

创建 `app/sitemap.ts`，Next.js 会在构建时自动产出 `/sitemap.xml`，与 robots.txt 中已声明的地址一致。

```ts
// app/sitemap.ts
import type { MetadataRoute } from "next";

const BASE = "https://brain.mangofolio.com";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticRoutes = ["", "/openapi", "/settings"].map((path) => ({
    url: `${BASE}${path}`,
    lastmod: new Date().toISOString(),
    changefreq: "weekly" as const,
    priority: path === "" ? 1 : 0.7,
  }));

  // 若后续开通博客，把文章 URL 也加进来：
  // const posts = await getBlogPosts();
  // const postRoutes = posts.map(p => ({ url: `${BASE}/learn/${p.slug}`, ... }));

  return [...staticRoutes /*, ...postRoutes */];
}
```

上线后用 `https://brain.mangofolio.com/sitemap.xml` 验证（应返回 XML，不再 404）。

---

## 2. 全局 Metadata（修复 P0/P1：meta description + OG + Twitter + canonical）

在 `app/layout.tsx` 的 `metadata` 导出中补全。需先把 `og-image.png` 放到 `public/og-image.png`（1200×630）。

```ts
// app/layout.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  metadataBase: new URL("https://brain.mangofolio.com"),
  title: {
    default: "InvestBrain — 投资第二大脑 | 投资纪律与决策辅助",
    template: "%s | InvestBrain",
  },
  description:
    "InvestBrain 是你的投资第二大脑：用想法记录、16 位大师思想库、Socratic 投研教练与行为模式报告，帮你锚定投资纪律、映照真实自己。本地运行，数据不出电脑，不做投顾、不执行交易。",
  keywords: [
    "投资纪律", "投资第二大脑", "知行合一 投资", "投资复盘",
    "行为金融", "追涨杀跌", "投资大师思想", "投研教练", "投资 AI 工具",
  ],
  alternates: {
    canonical: "https://brain.mangofolio.com/",
  },
  openGraph: {
    type: "website",
    locale: "zh_CN",
    url: "https://brain.mangofolio.com/",
    siteName: "InvestBrain",
    title: "InvestBrain — 投资第二大脑",
    description:
      "锚定投资纪律，映照真实自己。想法记录 + 大师思想库 + 投研教练 + 行为模式报告，让规则替你决策。",
    images: [
      { url: "/og-image.png", width: 1200, height: 630, alt: "InvestBrain 投资第二大脑" },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "InvestBrain — 投资第二大脑",
    description: "锚定投资纪律，映照真实自己。本地运行的投资决策辅助工具。",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, "max-image-preview": "large" },
  },
};
```

---

## 3. 结构化数据 JSON-LD（修复 P1：富摘要）

### 3.1 通用注入组件

```tsx
// components/JsonLd.tsx
export function JsonLd({ data }: { data: Record<string, unknown> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
```

### 3.2 首页 Organization + WebSite + SoftwareApplication + FAQPage

在 `app/page.tsx` 顶部（或 layout）注入：

```tsx
import { JsonLd } from "@/components/JsonLd";

const org = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "mangoFolio",
  url: "https://brain.mangofolio.com",
  logo: "https://brain.mangofolio.com/logo.png",
};

const webSite = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "InvestBrain",
  url: "https://brain.mangofolio.com",
};

const software = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "InvestBrain",
  operatingSystem: "Web / Local (MCP)",
  applicationCategory: "FinanceApplication",
  description:
    "投资第二大脑：想法记录、大师思想库、Socratic 投研教练、行为模式报告。本地存储，不做投顾。",
  offers: { "@type": "Offer", price: "0", priceCurrency: "CNY" },
};

const faq = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "InvestBrain 如何使用？",
      acceptedAnswer: {
        "@type": "Answer",
        text: "安装后运行 MCP Server，通过自然语言交互：记录想法、查询大师、设置提醒、生成行为模式报告。也可在 Skill 市场复制 Prompt 给任意 AI 使用。",
      },
    },
    {
      "@type": "Question",
      name: "数据安全吗？",
      acceptedAnswer: {
        "@type": "Answer",
        text: "完全本地存储。SQLite 数据库保存在本地，不上传任何云端服务器，不连接券商账户，不执行任何交易。",
      },
    },
    {
      "@type": "Question",
      name: "InvestBrain 和投顾有什么区别？",
      acceptedAnswer: {
        "@type": "Answer",
        text: "不做交易执行、不做收费投顾、不提供选股建议。Brain 是镜子 + 纪律锚点，帮你思考而非替你决策。",
      },
    },
  ],
};

// 在组件 return 中：
// <JsonLd data={org} /><JsonLd data={webSite} /><JsonLd data={software} /><JsonLd data={faq} />
```

---

## 4. robots.txt（保持现有，确认一致）

现有 `public/robots.txt` 已正确，无需改；只需确保 sitemap 地址与第 1 步产出一致：

```
User-agent: *
Allow: /

Sitemap: https://brain.mangofolio.com/sitemap.xml
```

> 若改用 Next.js `app/robots.ts` 也能生成，但静态文件已存在且正确，建议保留静态文件，避免重复。

---

## 5. og-image.png（社交预览图，当前缺失）

- 把 1200×630 的 `og-image.png` 放入 `public/og-image.png`。
- 同款可参考已为 FinancePro 生成的图（深蓝 + 青色，主视觉建议「锚 / 镜子」意象）。
- 需要我直接为 Brain 出一张，说一声即可（沿用本策略报告末尾的设计建议）。

---

## 6. 上线后必做（P0 收尾）

1. 部署后访问 `https://brain.mangofolio.com/sitemap.xml` 确认不再是 404。
2. 注册并验证 **Google Search Console** 与 **百度站长平台**，提交 sitemap。
3. 用 Rich Results Test 校验 FAQ / SoftwareApplication JSON-LD 无报错。
4. 用 Open Graph Debugger（Facebook / LinkedIn）确认分享卡片正常抓取 og-image。

---

## 7. 修复工时估算

| 项 | 工时 |
|----|------|
| sitemap.ts + GSC 注册 | 1h |
| metadata（description/OG/Twitter/canonical） | 2h |
| JSON-LD 注入 | 2h |
| og-image.png 生成（如需我出） | 0.5h |
| 博客/指南中心（后续内容） | 持续 |
| **合计（技术止血）** | **~8h** |
