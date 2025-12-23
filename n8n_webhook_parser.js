// 🔥 N8N WEBHOOK PARSER v3
// Парсит webhook payload и валидирует depth_level
// ⚠️ НЕ отправляет depth_level_description в GitHub (он её не ожидает)

// Получи данные из Webhook
const payload = $input.item.json.body || {};

// URL валидация
const url = String(payload.url || 'https://callmedley.com').trim();
if (!url.startsWith('http://') && !url.startsWith('https://')) {
  throw new Error(`Invalid URL: ${url}. Must start with http:// or https://`);
}

// ⭐ depth_level валидация
const depthLevelStr = String(payload.depth_level || '2').trim();
const depthLevel = parseInt(depthLevelStr, 10);

if (isNaN(depthLevel) || depthLevel < 1 || depthLevel > 4) {
  throw new Error(
    `depth_level must be 1-4, got ${depthLevelStr}.\n` +
    `Levels:\n` +
    `  1 = Start page only (fast)\n` +
    `  2 = Start + direct children (recommended)\n` +
    `  3 = Start + 2 levels deep\n` +
    `  4 = Very deep crawl (slow, be careful!)`
  );
}

// Output directory (optional, sanitized)
const outputDir = String(payload.output_dir || 'site_archive').trim()
  .replace(/[^a-zA-Z0-9_-]/g, ''); // Sanitize

if (outputDir.length === 0) {
  throw new Error('output_dir is empty after sanitization');
}

// ✅ Return validated payload (ТОЛЬКО эти параметры!)
// GitHub workflow ожидает ТОЛЬКО: url, output_dir, depth_level, resumeUrl
return {
  url,
  depth_level: String(depthLevel),  // Convert to string for GitHub API
  output_dir: outputDir
  // НЕ добавляй depth_level_description! GitHub workflow её не знает
  // НЕ добавляй resumeUrl сюда! Передавай отдельно через {{ $resumeWebhookUrl }}
};
